import re
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


ROOT_DIR = Path(__file__).resolve().parents[1]
SOURCES_FILE = ROOT_DIR / "research" / "sources.md"
OUTPUT_DIR = ROOT_DIR / "research" / "linkedin-posts"
REPORT_FILE = OUTPUT_DIR / "linkedin-report.md"
PROMPT_FILE = OUTPUT_DIR / "linkedin-posts-prompt.md"

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


@dataclass
class Expert:
    name: str
    linkedin_url: str
    slug: str


@dataclass
class Post:
    title: str
    url: str
    publish_date: str
    content: str
    source: str
    profile_photo_url: str
    profile_banner_url: str
    post_image_urls: List[str]
    carousel_slide_urls: List[str]
    video_thumbnail_url: str
    document_preview_url: str
    reactions: str
    comments: str
    reposts: str


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
        if not line.startswith("|"):
            continue
        if line.strip().startswith("| ---"):
            continue
        if line.strip().startswith("| No"):
            continue
        cells = [part.strip() for part in line.split("|")[1:-1]]
        if len(cells) < 3:
            continue
        expert_name = cells[1]
        linkedin_url = extract_markdown_link(cells[2])
        if linkedin_url and "linkedin.com" in linkedin_url:
            experts.append(
                Expert(name=expert_name, linkedin_url=linkedin_url, slug=slugify(expert_name))
            )
    return experts


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def unique_preserve_order(values: List[str]) -> List[str]:
    seen: Set[str] = set()
    ordered: List[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def profile_slug_from_url(linkedin_url: str) -> str:
    path = linkedin_url.rstrip("/").split("linkedin.com/")[-1]
    path = path.split("?")[0]
    parts = [p for p in path.split("/") if p]
    return parts[-1] if parts else ""


def extract_profile_media_from_html(soup: BeautifulSoup, base_url: str) -> Tuple[str, str]:
    profile_photo = ""
    banner = ""

    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        profile_photo = urljoin(base_url, og_image.get("content", "").strip())

    banner_meta = soup.find("meta", property="linkedin:cover_image")
    if banner_meta and banner_meta.get("content"):
        banner = urljoin(base_url, banner_meta.get("content", "").strip())

    return profile_photo, banner


def extract_visible_posts_from_html(html: str, base_url: str) -> List[Post]:
    soup = BeautifulSoup(html, "html.parser")
    profile_photo, profile_banner = extract_profile_media_from_html(soup, base_url)
    posts: List[Post] = []

    # Extract candidate links containing activity/update/share markers.
    candidate_links = soup.select(
        "a[href*='/feed/update/'], a[href*='/posts/'], a[href*='/activity/']"
    )
    seen: set = set()

    for link in candidate_links:
        href = link.get("href", "").strip()
        if not href:
            continue
        url = urljoin(base_url, href)
        if url in seen:
            continue
        seen.add(url)

        container = link.find_parent(["article", "li", "div", "section"])
        content = ""
        if container:
            content = clean_text(container.get_text(" ", strip=True))
        if not content:
            content = clean_text(link.get_text(" ", strip=True))
        if not content:
            continue

        # Preserve visible relative date labels when exact date is unavailable.
        date_label = "Unknown"
        if container:
            date_pattern = re.search(
                r"\b(\d+\s*[smhdw]\.?|yesterday|today|just now|\d+\s+days? ago|\d+\s+weeks? ago)\b",
                content.lower(),
            )
            if date_pattern:
                date_label = date_pattern.group(0)

        post_images: List[str] = []
        carousel_images: List[str] = []
        video_thumbnail = ""
        document_preview = ""
        reactions = "Not displayed on public page"
        comments = "Not displayed on public page"
        reposts = "Not displayed on public page"

        if container:
            for image in container.select("img[src], img[data-delayed-url], img[data-ghost-url]"):
                src = (
                    image.get("src")
                    or image.get("data-delayed-url")
                    or image.get("data-ghost-url")
                    or ""
                ).strip()
                if src:
                    full_src = urljoin(base_url, src)
                    alt = (image.get("alt") or "").lower()
                    if any(token in alt for token in ("video", "play")) and not video_thumbnail:
                        video_thumbnail = full_src
                    elif any(token in alt for token in ("document", "pdf", "slide")):
                        document_preview = full_src
                    elif "carousel" in alt or "slide" in alt:
                        carousel_images.append(full_src)
                    else:
                        post_images.append(full_src)

            for source in container.select("source[src]"):
                if source.get("src"):
                    video_thumbnail = video_thumbnail or urljoin(base_url, source["src"])

            text = content.lower()
            reactions_match = re.search(
                r"((?:\d[\d,\.]*|one|two|three|four|five|six|seven|eight|nine|ten)\s*(?:reactions?|likes?))",
                text,
            )
            comments_match = re.search(
                r"((?:\d[\d,\.]*|one|two|three|four|five|six|seven|eight|nine|ten)\s*comments?)",
                text,
            )
            reposts_match = re.search(
                r"((?:\d[\d,\.]*|one|two|three|four|five|six|seven|eight|nine|ten)\s*(?:reposts?|shares?))",
                text,
            )
            if reactions_match:
                reactions = reactions_match.group(1)
            if comments_match:
                comments = comments_match.group(1)
            if reposts_match:
                reposts = reposts_match.group(1)

        title = content[:90] + ("..." if len(content) > 90 else "")
        posts.append(
            Post(
                title=title if title else "LinkedIn Post",
                url=url,
                publish_date=date_label,
                content=content,
                source="Public LinkedIn HTML",
                profile_photo_url=profile_photo,
                profile_banner_url=profile_banner,
                post_image_urls=unique_preserve_order(post_images),
                carousel_slide_urls=unique_preserve_order(carousel_images),
                video_thumbnail_url=video_thumbnail,
                document_preview_url=document_preview,
                reactions=reactions,
                comments=comments,
                reposts=reposts,
            )
        )
        if len(posts) >= 5:
            break

    # Preserve natural extracted order (typically newest -> oldest), avoid duplicates.
    unique_posts: List[Post] = []
    seen_urls: Set[str] = set()
    for post in posts:
        if post.url in seen_urls:
            continue
        seen_urls.add(post.url)
        unique_posts.append(post)
    return unique_posts


def try_fetch_linkedin_posts(linkedin_url: str) -> Tuple[List[Post], Optional[str]]:
    session = requests.Session()
    session.headers.update(REQUEST_HEADERS)

    slug = profile_slug_from_url(linkedin_url)
    candidate_urls = [
        linkedin_url,
        f"https://www.linkedin.com/in/{slug}/recent-activity/all/",
        f"https://www.linkedin.com/in/{slug}/details/recent-activity/shares/",
    ]

    best_error = "No public post data found."
    for url in candidate_urls:
        try:
            response = session.get(url, timeout=25, allow_redirects=True)
            if response.status_code >= 400:
                best_error = f"HTTP {response.status_code} while fetching {url}"
                time.sleep(1.2)
                continue

            html = response.text
            if "authwall" in response.url or "checkpoint/challenge" in response.url:
                best_error = "LinkedIn auth wall blocked public access."
                time.sleep(1.2)
                continue

            posts = extract_visible_posts_from_html(html, response.url)
            if posts:
                return posts[:5], None
            best_error = "No visible public posts found on fetched page."
            time.sleep(1.2)
        except requests.RequestException as error:
            best_error = f"Request failed: {error}"
            time.sleep(1.2)

    return [], best_error


def write_post_file(
    file_path: Path,
    expert_name: str,
    post_title: str,
    post_url: str,
    publish_date: str,
    source: str,
    post_content: Optional[str],
    media_profile_photo_url: str,
    media_profile_banner_url: str,
    media_post_image_urls: List[str],
    media_carousel_slide_urls: List[str],
    media_video_thumbnail_url: str,
    media_document_preview_url: str,
    reactions: str,
    comments: str,
    reposts: str,
    failure_reason: Optional[str] = None,
) -> None:
    lines = [
        f"# Expert Name: {expert_name}",
        f"# Post Title: {post_title}",
        f"# Post URL: {post_url}",
        f"# Publish Date: {publish_date}",
        f"# Content Source: {source}",
        "",
        "## Post Content",
        "",
    ]
    if post_content:
        lines.append(post_content)
    else:
        message = "Post unavailable."
        if failure_reason:
            message += f"\n\nReason: {failure_reason}"
        lines.append(message)
    media_lines = ["", "## Media Assets", ""]
    if media_profile_photo_url:
        media_lines.append(f"* Profile Photo URL: {media_profile_photo_url}")
    if media_profile_banner_url:
        media_lines.append(f"* Profile Banner URL: {media_profile_banner_url}")
    if media_post_image_urls:
        media_lines.append(f"* Post Image URL(s): {', '.join(media_post_image_urls)}")
    if media_carousel_slide_urls:
        media_lines.append(
            f"* Carousel Slide Image URL(s): {', '.join(media_carousel_slide_urls)}"
        )
    if media_video_thumbnail_url:
        media_lines.append(f"* Video Thumbnail URL: {media_video_thumbnail_url}")
    if media_document_preview_url:
        media_lines.append(
            f"* Attached Document Preview URL: {media_document_preview_url}"
        )
    lines.extend(media_lines)
    lines.extend(
        [
            "",
            "## Engagement Data",
            "",
            f"* Likes / Reactions: {reactions}",
            f"* Comments: {comments}",
            f"* Reposts: {reposts}",
        ]
    )
    file_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def save_prompt_record() -> None:
    prompt_text = """Use the existing repository structure exactly as it is.

Read source data from:

research/sources.md

Your task is to collect recent LinkedIn content only.

FOCUS:
Use only experts that have a valid LinkedIn link in the LinkedIn column.

Ignore YouTube for this task.

OUTPUT LOCATION:

research/linkedin-posts/

Do NOT create any new root folders.
Do NOT move existing files.

ORGANIZATION RULE:

Store LinkedIn posts organized by author.

Create one folder per expert inside:

research/linkedin-posts/

Use clean slug folder names such as:

research/linkedin-posts/aleyda-solis/
research/linkedin-posts/matt-diggity/
research/linkedin-posts/kevin-indig/

Inside each expert folder, save post files as:

post-01.md
post-02.md
post-03.md

Collect the latest 5 recent posts per expert.

FILE CONTENT FORMAT:

# Expert Name
# Post Title (if available)
# Post URL
# Publish Date
# Content Source

## Post Content

(full visible post text)

If full text is unavailable, capture the visible text only.

## Media Assets

* Profile Photo URL
* Profile Banner URL
* Post Image URL(s)
* Carousel Slide Image URL(s)
* Video Thumbnail URL
* Attached Document Preview URL

(Only include fields where data exists. Do not write unavailable, none, N/A, or empty placeholders.)

## Engagement Data

* Likes / Reactions
* Comments
* Reposts

(Required for every post. Extract displayed values exactly as shown.)

IF POST NOT AVAILABLE:

Create the file and write:

Post unavailable.

Include reason if known.

RULES:

1. Use scraping methods to collect publicly available LinkedIn content.
2. Read all valid LinkedIn links from research/sources.md and process them automatically in batch.
3. Keep filenames clean and consistent.
4. Use slug folder names.
5. Do NOT edit sources.md.
6. Do NOT process experts without LinkedIn links.
7. Keep markdown neat and professional.
8. Respect rate limits and avoid excessive requests.
9. Expand hidden text such as “see more” whenever possible.
10. Capture lazy-loaded images and dynamically loaded media assets.
11. If multiple images exist in one post, collect all.
12. Preserve original post ordering from newest to oldest.
13. Avoid duplicate posts.
14. If exact publish date unavailable, capture displayed relative date.
15. Do not print missing-field labels. Omit missing fields entirely.
16. Engagement Data section must always exist in every post file.

PROJECT VISIBILITY:

Ensure the process is clear and professional through existing project files:

- Keep requirements.txt updated with needed Python packages.
- Keep .gitignore clean and ensure sensitive files like .env are ignored.
- Keep repository structure organized and readable.

PROMPT RECORD:

Save the exact prompt used for this run as:

research/linkedin-posts/linkedin-posts-prompt.md

FINAL REPORT:

Display final summary in output and also save it as:

research/linkedin-posts/linkedin-report.md

Include:

- Experts processed
- Posts processed
- Successful posts collected
- Failed collections
- Files created
* Total media assets collected
* Experts with inaccessible LinkedIn pages
* Notes on missing data or scraping limitations
"""
    PROMPT_FILE.write_text(prompt_text.strip() + "\n", encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    experts = parse_experts_from_sources(SOURCES_FILE)
    save_prompt_record()

    experts_processed = 0
    posts_processed = 0
    successful_collections = 0
    failed_collections = 0
    total_media_assets_collected = 0
    inaccessible_experts: List[str] = []
    missing_data_notes: List[str] = []
    files_created: List[str] = [str(PROMPT_FILE.relative_to(ROOT_DIR))]

    for expert in experts:
        experts_processed += 1
        expert_dir = OUTPUT_DIR / expert.slug
        expert_dir.mkdir(parents=True, exist_ok=True)

        posts, error_message = try_fetch_linkedin_posts(expert.linkedin_url)
        if posts:
            for index in range(1, 6):
                output_file = expert_dir / f"post-{index:02d}.md"
                if index <= len(posts):
                    post = posts[index - 1]
                    write_post_file(
                        file_path=output_file,
                        expert_name=expert.name,
                        post_title=post.title,
                        post_url=post.url,
                        publish_date=post.publish_date,
                        source=post.source,
                        post_content=post.content,
                        media_profile_photo_url=post.profile_photo_url,
                        media_profile_banner_url=post.profile_banner_url,
                        media_post_image_urls=post.post_image_urls,
                        media_carousel_slide_urls=post.carousel_slide_urls,
                        media_video_thumbnail_url=post.video_thumbnail_url,
                        media_document_preview_url=post.document_preview_url,
                        reactions=post.reactions,
                        comments=post.comments,
                        reposts=post.reposts,
                    )
                    posts_processed += 1
                    successful_collections += 1
                    total_media_assets_collected += (
                        (1 if post.profile_photo_url else 0)
                        + (1 if post.profile_banner_url else 0)
                        + len(post.post_image_urls)
                        + len(post.carousel_slide_urls)
                        + (1 if post.video_thumbnail_url else 0)
                        + (1 if post.document_preview_url else 0)
                    )
                else:
                    write_post_file(
                        file_path=output_file,
                        expert_name=expert.name,
                        post_title="Post unavailable",
                        post_url=expert.linkedin_url,
                        publish_date="Unknown",
                        source="Public LinkedIn HTML",
                        post_content=None,
                        media_profile_photo_url="",
                        media_profile_banner_url="",
                        media_post_image_urls=[],
                        media_carousel_slide_urls=[],
                        media_video_thumbnail_url="",
                        media_document_preview_url="",
                        reactions="Not displayed on public page",
                        comments="Not displayed on public page",
                        reposts="Not displayed on public page",
                        failure_reason="Fewer than 5 public posts were available.",
                    )
                    posts_processed += 1
                    failed_collections += 1
                files_created.append(str(output_file.relative_to(ROOT_DIR)))
        else:
            for index in range(1, 6):
                output_file = expert_dir / f"post-{index:02d}.md"
                write_post_file(
                    file_path=output_file,
                    expert_name=expert.name,
                    post_title="Post unavailable",
                    post_url=expert.linkedin_url,
                    publish_date="Unknown",
                    source="Public LinkedIn HTML",
                    post_content=None,
                    media_profile_photo_url="",
                    media_profile_banner_url="",
                    media_post_image_urls=[],
                    media_carousel_slide_urls=[],
                    media_video_thumbnail_url="",
                    media_document_preview_url="",
                    reactions="Not displayed on public page",
                    comments="Not displayed on public page",
                    reposts="Not displayed on public page",
                    failure_reason=error_message or "Unknown error",
                )
                posts_processed += 1
                failed_collections += 1
                files_created.append(str(output_file.relative_to(ROOT_DIR)))
            inaccessible_experts.append(expert.name)
            missing_data_notes.append(
                f"{expert.name}: {error_message or 'Unknown public-access limitation.'}"
            )

        time.sleep(1.5)

    report_lines = [
        "# LinkedIn Posts Collection Report",
        "",
        f"- Experts processed: {experts_processed}",
        f"- Posts processed: {posts_processed}",
        f"- Successful posts collected: {successful_collections}",
        f"- Failed collections: {failed_collections}",
        f"- Total media assets collected: {total_media_assets_collected}",
        (
            "- Experts with inaccessible LinkedIn pages: "
            + (", ".join(inaccessible_experts) if inaccessible_experts else "None")
        ),
        "",
        "## Notes on missing data or scraping limitations",
    ]
    if missing_data_notes:
        report_lines.extend(f"- {note}" for note in missing_data_notes)
    else:
        report_lines.append("- No major limitations encountered in this run.")
    report_lines.extend(
        [
        "",
        "## Files created",
        ]
    )
    report_lines.extend(f"- {item}" for item in files_created)

    REPORT_FILE.write_text("\n".join(report_lines).strip() + "\n", encoding="utf-8")
    print("\n".join(report_lines))


if __name__ == "__main__":
    main()
