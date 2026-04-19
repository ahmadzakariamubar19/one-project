import os
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import requests
from dotenv import load_dotenv
from yt_dlp import YoutubeDL
from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    YouTubeTranscriptApi,
)


ROOT_DIR = Path(__file__).resolve().parents[1]
SOURCES_FILE = ROOT_DIR / "research" / "sources.md"
OUTPUT_DIR = ROOT_DIR / "research" / "youtube-transcripts"
REPORT_FILE = OUTPUT_DIR / "youtube-report.md"


@dataclass
class Expert:
    name: str
    youtube_url: str
    slug: str


@dataclass
class VideoItem:
    title: str
    url: str
    publish_date: str
    video_id: str


def slugify(value: str) -> str:
    normalized = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    clean = re.sub(r"[^\w\s-]", "", normalized, flags=re.UNICODE).strip().lower()
    clean = re.sub(r"[\s_-]+", "-", clean)
    return clean.strip("-")


def extract_markdown_link(text: str) -> str:
    match = re.search(r"\((https?://[^\s)]+)\)", text)
    if match:
        return match.group(1)
    raw_url = re.search(r"(https?://\S+)", text)
    return raw_url.group(1) if raw_url else ""


def parse_experts_from_sources(file_path: Path) -> List[Expert]:
    content = file_path.read_text(encoding="utf-8")
    experts: List[Expert] = []
    for line in content.splitlines():
        if not line.startswith("|") or "---" in line or "Expert" in line:
            continue
        cells = [part.strip() for part in line.split("|")[1:-1]]
        if len(cells) < 4:
            continue
        expert_name = cells[1]
        youtube_cell = cells[3]
        youtube_url = extract_markdown_link(youtube_cell)
        if not youtube_url or "youtube.com" not in youtube_url:
            continue
        experts.append(
            Expert(name=expert_name, youtube_url=youtube_url, slug=slugify(expert_name))
        )
    return experts


def get_latest_videos(channel_url: str, limit: int = 2) -> List[VideoItem]:
    query_url = channel_url if channel_url.endswith("/videos") else f"{channel_url}/videos"
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "playlistend": limit,
        "skip_download": True,
        "ignoreerrors": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query_url, download=False)

    entries = info.get("entries", []) if info else []
    videos: List[VideoItem] = []
    for item in entries:
        if not item:
            continue
        video_id = item.get("id", "")
        title = item.get("title", "Untitled Video")
        webpage_url = item.get("url", "")
        if webpage_url and not webpage_url.startswith("http"):
            webpage_url = f"https://www.youtube.com/watch?v={webpage_url}"
        publish_date = item.get("upload_date", "Unknown")
        if publish_date and publish_date != "Unknown" and len(publish_date) == 8:
            publish_date = f"{publish_date[0:4]}-{publish_date[4:6]}-{publish_date[6:8]}"
        if webpage_url and video_id:
            videos.append(
                VideoItem(
                    title=title,
                    url=webpage_url,
                    publish_date=publish_date,
                    video_id=video_id,
                )
            )
        if len(videos) >= limit:
            break
    return videos


def fetch_supadata_transcript(
    video_url: str, supadata_api_key: str
) -> Tuple[Optional[str], str]:
    if not supadata_api_key:
        return None, "Supadata API key missing"

    endpoint = "https://api.supadata.ai/v1/youtube/transcript"
    headers = {"x-api-key": supadata_api_key}
    params = {"url": video_url}
    try:
        response = requests.get(endpoint, headers=headers, params=params, timeout=45)
        if response.status_code != 200:
            return None, f"Supadata request failed ({response.status_code})"
        payload = response.json()
        if isinstance(payload, dict):
            for key in ("content", "transcript", "text"):
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip(), "Supadata"
                if isinstance(value, list):
                    stitched = " ".join(
                        part.get("text", "")
                        for part in value
                        if isinstance(part, dict) and part.get("text")
                    ).strip()
                    if stitched:
                        return stitched, "Supadata"
        return None, "Supadata returned empty transcript"
    except requests.RequestException as error:
        return None, f"Supadata error: {error}"


def fetch_free_transcript(video_id: str) -> Tuple[Optional[str], str]:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = "\n".join(chunk.get("text", "") for chunk in transcript).strip()
        if transcript_text:
            return transcript_text, "youtube-transcript-api"
        return None, "youtube-transcript-api returned empty transcript"
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as error:
        return None, f"Free method unavailable: {error.__class__.__name__}"
    except Exception as error:  # pylint: disable=broad-except
        return None, f"Free method error: {error}"


def write_video_file(
    file_path: Path,
    expert_name: str,
    video_title: str,
    video_url: str,
    publish_date: str,
    source: str,
    transcript: Optional[str],
    failure_reason: Optional[str] = None,
) -> None:
    lines = [
        f"# Expert Name: {expert_name}",
        f"# Video Title: {video_title}",
        f"# Video URL: {video_url}",
        f"# Publish Date: {publish_date}",
        f"# Transcript Source: {source}",
        "",
        "## Transcript",
        "",
    ]
    if transcript:
        lines.append(transcript)
    else:
        message = "Transcript unavailable."
        if failure_reason:
            message += f"\n\nReason: {failure_reason}"
        lines.append(message)
    file_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main() -> None:
    load_dotenv(ROOT_DIR / ".env")
    supadata_api_key = os.getenv("SUPADATA_API_KEY", "").strip()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    experts = parse_experts_from_sources(SOURCES_FILE)

    processed_experts = 0
    videos_processed = 0
    successful_transcripts = 0
    failed_transcripts = 0
    created_files: List[str] = []

    for expert in experts:
        processed_experts += 1
        expert_dir = OUTPUT_DIR / expert.slug
        expert_dir.mkdir(parents=True, exist_ok=True)

        videos = get_latest_videos(expert.youtube_url, limit=2)
        if not videos:
            fallback_file = expert_dir / "video-01.md"
            write_video_file(
                file_path=fallback_file,
                expert_name=expert.name,
                video_title="No recent video found",
                video_url=expert.youtube_url,
                publish_date="Unknown",
                source="N/A",
                transcript=None,
                failure_reason="Could not retrieve videos from channel.",
            )
            created_files.append(str(fallback_file.relative_to(ROOT_DIR)))
            failed_transcripts += 1
            continue

        for index, video in enumerate(videos, start=1):
            videos_processed += 1
            transcript, source = fetch_supadata_transcript(video.url, supadata_api_key)
            failure_reason = None
            if not transcript:
                transcript, free_source = fetch_free_transcript(video.video_id)
                source = free_source
            if not transcript:
                failure_reason = source
                failed_transcripts += 1
                source = "N/A"
            else:
                successful_transcripts += 1

            output_file = expert_dir / f"video-{index:02d}.md"
            write_video_file(
                file_path=output_file,
                expert_name=expert.name,
                video_title=video.title,
                video_url=video.url,
                publish_date=video.publish_date,
                source=source,
                transcript=transcript,
                failure_reason=failure_reason,
            )
            created_files.append(str(output_file.relative_to(ROOT_DIR)))

    report_lines = [
        "# YouTube Transcript Collection Report",
        "",
        f"- Experts processed: {processed_experts}",
        f"- Videos processed: {videos_processed}",
        f"- Successful transcripts: {successful_transcripts}",
        f"- Failed transcripts: {failed_transcripts}",
        "",
        "## Files created",
    ]
    if created_files:
        report_lines.extend(f"- {path}" for path in created_files)
    else:
        report_lines.append("- No files created")

    REPORT_FILE.write_text("\n".join(report_lines).strip() + "\n", encoding="utf-8")
    print("\n".join(report_lines))


if __name__ == "__main__":
    main()
