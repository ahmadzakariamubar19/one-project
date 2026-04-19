Use the existing repository structure exactly as it is.

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
