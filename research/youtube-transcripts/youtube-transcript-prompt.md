Use the existing repository structure exactly as it is.

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