Use the existing repository structure exactly as it is.

Read source data from:

research/sources.md

Your task is to collect recent YouTube transcripts only.

FOCUS:
Use only experts that have a valid YouTube link in the YouTube column.

Ignore LinkedIn for this task.

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

# Expert Name

# Video Title

# Video URL

# Publish Date

# Transcript Source

## Transcript

If timestamp data is available, include timestamps in this format:

[00:00] transcript text
[00:15] transcript text
[01:02] transcript text

If timestamp data is unavailable, provide clean plain transcript text.

(full transcript text)

IF TRANSCRIPT NOT AVAILABLE:

Create the file and write:

Transcript unavailable.

Include reason if known.

RULES:

1. Use APIs such as Supadata or other free transcript methods.
2. Use my existing API key from .env if available.
3. Read all valid YouTube links from research/sources.md and process them automatically in batch.
4. Keep filenames clean and consistent.
5. Use slug folder names.
6. Do NOT edit sources.md.
7. Do NOT process experts without YouTube links.
8. Keep markdown neat and professional.

PROJECT VISIBILITY:

Ensure the process is clear and professional through existing project files:

- Keep requirements.txt updated with needed Python packages.
- Keep .gitignore clean and ensure sensitive files like .env are ignored.
- Use .env for API keys or secrets.
- Keep repository structure organized and readable.

PROMPT RECORD:

Save the exact prompt used for this run as:

research/youtube-transcripts/youtube-transcript-prompt.md

FINAL REPORT:

Display final summary in output and also save it as:

research/youtube-transcripts/youtube-report.md

Include:

- Experts processed
- Videos processed
- Successful transcripts
- Failed transcripts
- Files created