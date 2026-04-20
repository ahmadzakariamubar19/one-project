import os
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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
PROMPT_FILE = OUTPUT_DIR / "youtube-transcript-prompt.md"


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
    duration_seconds: Optional[int] = None


@dataclass
class TranscriptResult:
    text: str
    source: str
    segment_count: int
    coverage_seconds: int


RUN_PROMPT = """Use the existing repository structure exactly as it is.

Read source data from:

research/sources.md

Your task is to collect recent YouTube transcripts only.

FOCUS:
Use only experts that have a valid YouTube link in the YouTube column.

Ignore LinkedIn for this task.

IMPORTANT (FULL TRANSCRIPT RULE):
You MUST fetch COMPLETE FULL transcripts for every video.
Do NOT return partial, preview, or truncated transcripts.
Do NOT summarize or shorten content.
Ensure the transcript covers the entire duration of the video from start to end.

TRANSCRIPT SOURCE STRATEGY (IMPORTANT):

Do NOT rely only on Supadata.

You MUST use a fallback system in this order:

1. Primary: Supadata API (if available and working)
2. Secondary: youtube-transcript-api (Python library)
3. Tertiary: yt-dlp auto-generated subtitles

If one method fails or returns partial transcript:
- Automatically retry using the next method
- Do NOT stop after first failure
- Ensure final output is FULL transcript before marking success

If transcript is returned in segments or chunks:
- You MUST iterate through ALL segments
- You MUST concatenate all segments in correct chronological order
- You MUST NOT stop after the first chunk

Validate that transcript length is proportional to video duration.

OUTPUT LOCATION:

research/youtube-transcripts/

Do NOT create any new root folders.
Do NOT move existing files.

ORGANIZATION RULE:

Store transcripts organized by video.

Create one folder per expert inside:

research/youtube-transcripts/

Use clean slug folder names such as:

research/youtube-transcripts/aleyda-solis/
research/youtube-transcripts/matt-diggity/
research/youtube-transcripts/nathan-gotch/

Inside each expert folder, save video transcript files as:

video-01.md
video-02.md

Collect latest 5 recent videos per expert.

FILE CONTENT FORMAT:

Expert Name

Video Title

Video URL

Publish Date

Transcript Source

Transcript

If timestamp data is available, include timestamps in this format:

- Timestamps MUST be normalized to HH:MM:SS format
- Convert all raw second-based timestamps into standard format

Example format:

[00:00:00] transcript text
[00:00:15] transcript text
[00:01:02] transcript text

Rules:
- Do not use raw second values like [12321:20]
- Always convert timestamps into proper HH:MM:SS format
- Ensure timestamps are sequential and consistent.

(full transcript text)

IF TRANSCRIPT NOT AVAILABLE:

Create the file and write:

Transcript unavailable.

Include reason if known.

RULES:

Use APIs such as Supadata or other free transcript methods.

Use my existing API key from .env if available.

Ensure .env is loaded correctly before API calls.

Read all valid YouTube links from research/sources.md and process them automatically in batch.

Keep filenames clean and consistent.

Use slug folder names.

Do NOT edit sources.md.

Do NOT process experts without YouTube links.

Keep markdown neat and professional.

PROJECT VISIBILITY:

Ensure the process is clear and professional through existing project files:

Keep requirements.txt updated with needed Python packages.

Keep .gitignore clean and ensure sensitive files like .env are ignored.

Use .env for API keys or secrets.

Keep repository structure organized and readable.

PROMPT RECORD:

Save the exact prompt used for this run as:

research/youtube-transcripts/youtube-transcript-prompt.md

FINAL REPORT:

Display final summary in output and also save it as:

research/youtube-transcripts/youtube-report.md

Include:

Experts processed
Videos processed
Successful transcripts
Failed transcripts
Files created
"""


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
                    duration_seconds=(
                        int(item.get("duration")) if item.get("duration") else None
                    ),
                )
            )
        if len(videos) >= limit:
            break
    return videos


def format_timestamp(seconds: float) -> str:
    total = int(seconds)
    hours = total // 3600
    minutes = (total % 3600) // 60
    secs = total % 60
    return f"[{hours:02d}:{minutes:02d}:{secs:02d}]"


def normalize_timed_segments(segments: List[Dict]) -> Optional[TranscriptResult]:
    ordered: List[Dict] = sorted(
        [segment for segment in segments if isinstance(segment, dict)],
        key=lambda x: float(x.get("start") or x.get("offset") or x.get("from") or 0),
    )
    lines: List[str] = []
    segment_count = 0
    max_coverage = 0.0
    for segment in ordered:
        text = segment.get("text", "")
        if text is None:
            continue
        text = str(text)
        if text == "":
            continue
        segment_count += 1
        ts = (
            segment.get("start")
            or segment.get("offset")
            or segment.get("start_time")
            or segment.get("from")
        )
        duration = segment.get("duration") or segment.get("dur") or segment.get("length")
        segment_end = None
        if isinstance(ts, (int, float)):
            lines.append(f"{format_timestamp(float(ts))} {text}")
            if isinstance(duration, (int, float)):
                segment_end = float(ts) + float(duration)
            else:
                segment_end = float(ts)
        else:
            lines.append(text)
        if isinstance(segment_end, (int, float)):
            max_coverage = max(max_coverage, float(segment_end))

    if not lines:
        return None

    return TranscriptResult(
        text="\n".join(lines),
        source="",
        segment_count=segment_count,
        coverage_seconds=int(max_coverage),
    )


def fetch_supadata_transcript(
    video_url: str, supadata_api_key: str
) -> Tuple[Optional[TranscriptResult], str]:
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
                if isinstance(value, str) and value != "":
                    return (
                        TranscriptResult(
                            text=value,
                            source="Supadata",
                            segment_count=0,
                            coverage_seconds=0,
                        ),
                        "Supadata",
                    )
                if isinstance(value, list):
                    stitched = normalize_timed_segments(value)
                    if stitched:
                        stitched.source = "Supadata"
                        return stitched, "Supadata"
        return None, "Supadata returned empty transcript"
    except requests.RequestException as error:
        return None, f"Supadata error: {error}"


def fetch_free_transcript(video_id: str) -> Tuple[Optional[TranscriptResult], str]:
    try:
        transcript_items = YouTubeTranscriptApi().fetch(video_id)
        transcript = [
            {
                "text": getattr(item, "text", ""),
                "start": getattr(item, "start", 0),
                "duration": getattr(item, "duration", 0),
            }
            for item in transcript_items
        ]
        transcript_result = normalize_timed_segments(transcript)
        if transcript_result:
            transcript_result.source = "youtube-transcript-api"
            return transcript_result, "youtube-transcript-api"
        return None, "youtube-transcript-api returned empty transcript"
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as error:
        return None, f"Free method unavailable: {error.__class__.__name__}"
    except Exception as error:  # pylint: disable=broad-except
        return None, f"Free method error: {error}"


def _vtt_timestamp_to_seconds(raw: str) -> Optional[float]:
    text = raw.strip().replace(",", ".")
    if "." in text:
        left, right = text.split(".", maxsplit=1)
        frac = right
    else:
        left, frac = text, "0"
    parts = left.split(":")
    if len(parts) != 3:
        return None
    try:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])
        millis = float(f"0.{frac}")
    except ValueError:
        return None
    return float(hours * 3600 + minutes * 60 + seconds) + millis


def _parse_vtt_segments(vtt_text: str) -> List[Dict]:
    chunks = re.split(r"\n\s*\n", vtt_text.replace("\r\n", "\n").strip())
    results: List[Dict] = []
    for chunk in chunks:
        lines = [line for line in chunk.split("\n") if line.strip() != ""]
        if not lines:
            continue
        if lines[0].startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        if "-->" not in chunk:
            continue
        time_line_idx = 0
        if "-->" not in lines[0] and len(lines) > 1 and "-->" in lines[1]:
            time_line_idx = 1
        if "-->" not in lines[time_line_idx]:
            continue
        start_raw = lines[time_line_idx].split("-->", maxsplit=1)[0].strip()
        start_seconds = _vtt_timestamp_to_seconds(start_raw)
        if start_seconds is None:
            continue
        text_lines = lines[time_line_idx + 1 :]
        if not text_lines:
            continue
        text = " ".join(
            re.sub(r"<[^>]+>", "", t).strip() for t in text_lines if t.strip()
        ).strip()
        if not text:
            continue
        if results and results[-1].get("text") == text:
            continue
        results.append({"text": text, "start": start_seconds})
    return results


def fetch_ytdlp_auto_subtitles(video_url: str) -> Tuple[Optional[TranscriptResult], str]:
    try:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "writesubtitles": False,
            "writeautomaticsub": False,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
        if not info:
            return None, "yt-dlp returned no video info"
        subtitles = info.get("subtitles") or {}
        auto_subs = info.get("automatic_captions") or {}
        candidates = subtitles or auto_subs
        if not candidates:
            return None, "yt-dlp found no subtitles or auto-captions"

        lang_order = ["en", "en-US", "en-GB"]
        lang_keys = [k for k in lang_order if k in candidates] + [
            k for k in candidates.keys() if k not in lang_order
        ]
        subtitle_url = None
        for lang in lang_keys:
            tracks = candidates.get(lang) or []
            preferred = next(
                (t for t in tracks if str(t.get("ext", "")).lower() == "vtt"), None
            )
            chosen = preferred or (tracks[0] if tracks else None)
            if chosen and chosen.get("url"):
                subtitle_url = chosen["url"]
                break
        if not subtitle_url:
            return None, "yt-dlp subtitle track URL missing"

        response = requests.get(subtitle_url, timeout=45)
        if response.status_code != 200:
            return None, f"yt-dlp subtitle download failed ({response.status_code})"

        segments = _parse_vtt_segments(response.text)
        stitched = normalize_timed_segments(segments)
        if stitched:
            stitched.source = "yt-dlp auto subtitles"
            return stitched, "yt-dlp auto subtitles"
        return None, "yt-dlp subtitle parsing produced no transcript lines"
    except Exception as error:  # pylint: disable=broad-except
        return None, f"yt-dlp subtitle fallback error: {error}"


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


def passes_duration_check(
    transcript_result: TranscriptResult, video_duration_seconds: Optional[int]
) -> bool:
    if not video_duration_seconds or transcript_result.coverage_seconds <= 0:
        return True
    # Allow a practical tail gap for outros/music and segmentation variance.
    tail_gap = video_duration_seconds - transcript_result.coverage_seconds
    return tail_gap <= max(20, int(video_duration_seconds * 0.1))


def passes_density_check(transcript_text: str, video_duration_seconds: Optional[int]) -> bool:
    if not video_duration_seconds or video_duration_seconds <= 0:
        return True
    # Guardrail against shortened summaries: transcript text should scale with video length.
    # 4 visible chars/sec is conservative and still allows pauses/outros.
    min_chars = max(400, int(video_duration_seconds * 4))
    if len(transcript_text) < min_chars:
        return False

    # If timestamped, require a reasonable number of lines for the runtime.
    timestamped_lines = re.findall(
        r"^\[\d{2}:\d{2}:\d{2}\]\s", transcript_text, flags=re.MULTILINE
    )
    if timestamped_lines:
        min_lines = max(20, int(video_duration_seconds / 20))
        if len(timestamped_lines) < min_lines:
            return False
    return True


def main() -> None:
    load_dotenv(ROOT_DIR / ".env")
    supadata_api_key = os.getenv("SUPADATA_API_KEY", "").strip()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROMPT_FILE.write_text(RUN_PROMPT, encoding="utf-8")
    experts = parse_experts_from_sources(SOURCES_FILE)

    processed_experts = 0
    videos_processed = 0
    successful_transcripts = 0
    failed_transcripts = 0
    coverage_verified = 0
    coverage_failed = 0
    created_files: List[str] = []

    for expert in experts:
        processed_experts += 1
        expert_dir = OUTPUT_DIR / expert.slug
        expert_dir.mkdir(parents=True, exist_ok=True)

        videos = get_latest_videos(expert.youtube_url, limit=5)
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
            method_errors: List[str] = []
            transcript_result = None
            source = "N/A"
            failure_reason = None

            fallback_methods = [
                ("Supadata", lambda: fetch_supadata_transcript(video.url, supadata_api_key)),
                ("youtube-transcript-api", lambda: fetch_free_transcript(video.video_id)),
                ("yt-dlp auto subtitles", lambda: fetch_ytdlp_auto_subtitles(video.url)),
            ]
            for method_name, method_fn in fallback_methods:
                candidate, method_source = method_fn()
                if not candidate:
                    method_errors.append(f"{method_name}: {method_source}")
                    continue
                if not passes_duration_check(candidate, video.duration_seconds):
                    method_errors.append(
                        f"{method_name}: coverage ended at ~{candidate.coverage_seconds}s"
                    )
                    continue
                if not passes_density_check(candidate.text, video.duration_seconds):
                    method_errors.append(
                        f"{method_name}: transcript appears too short for duration"
                    )
                    continue
                transcript_result = candidate
                source = method_source
                coverage_verified += 1
                break

            if not transcript_result:
                coverage_failed += 1
                failure_reason = "; ".join(method_errors) if method_errors else source
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
                transcript=transcript_result.text if transcript_result else None,
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
        f"- Coverage verified: {coverage_verified}",
        f"- Coverage failed: {coverage_failed}",
        f"- Files created: {len(created_files) + 2}",
        "",
        "## Files created",
    ]
    report_lines.append(f"- {PROMPT_FILE.relative_to(ROOT_DIR)}")
    report_lines.append(f"- {REPORT_FILE.relative_to(ROOT_DIR)}")
    if created_files:
        report_lines.extend(f"- {path}" for path in created_files)
    else:
        report_lines.append("- No files created")

    REPORT_FILE.write_text("\n".join(report_lines).strip() + "\n", encoding="utf-8")
    print("\n".join(report_lines))


if __name__ == "__main__":
    main()
