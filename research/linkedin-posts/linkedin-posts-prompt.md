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
research/linkedin-posts/david-quaid/

Inside each expert folder, save post files as:

post-01.md
post-02.md
post-03.md

TARGET COLLECTION RULE:

Attempt to collect up to 5 accessible posts per expert.

Do NOT require the latest 5 strictly in sequence.

If one or more newest posts are unavailable, deleted, private, blocked, redirected, or inaccessible, skip them and continue scanning older posts until 5 accessible posts are collected or no more accessible posts are found.

Prioritize recency, but accessibility comes first.

FILE CONTENT FORMAT:

Expert Name

Post Title (if available)

Post URL

Publish Date

Content Source

Post Content

(full visible post text)

If full text is unavailable, capture the visible text only.

Media Assets

Profile Photo

Profile Banner

Post Image

Carousel Slide Image URL(s)

Video Thumbnail URL

Attached Document Preview URL

(Only include fields where data exists. Do not write unavailable, none, N/A, or empty placeholders.)

Engagement Data

Likes / Reactions

Comments

Reposts

(Required for every post. Extract displayed values exactly as shown.)

IF NO ACCESSIBLE POSTS FOUND:

Create folder and report in final summary.

RULES:

Use scraping methods to collect publicly available LinkedIn content.

Read all valid LinkedIn links from research/sources.md and process them automatically in batch.

Keep filenames clean and consistent.

Use slug folder names.

Do NOT edit sources.md.

Do NOT process experts without LinkedIn links.

Keep markdown neat and professional.

Respect rate limits and avoid excessive requests.

Expand hidden text such as “see more” whenever possible.

Capture lazy-loaded images and dynamically loaded media assets.

If multiple images exist in one post, collect all.

Preserve newest-to-oldest priority among accessible posts.

Avoid duplicate posts.

If exact publish date unavailable, capture displayed relative date.

Do not print missing-field labels. Omit missing fields entirely.

Engagement Data section must always exist in every post file.

Skip inaccessible posts silently and continue searching older accessible posts.

Stop only after 5 accessible posts are collected or no further accessible posts remain.

PROJECT VISIBILITY:

Ensure the process is clear and professional through existing project files:

Keep requirements.txt updated with needed Python packages.

Keep .gitignore clean and ensure sensitive files like .env are ignored.

Keep repository structure organized and readable.

PROMPT RECORD:

Save the exact prompt used for this run as:

research/linkedin-posts/linkedin-posts-prompt.md

FINAL REPORT:

Display final summary in output and also save it as:

research/linkedin-posts/linkedin-report.md

Include:

Experts processed

Experts with at least one accessible post

Posts processed

Successful posts collected

Inaccessible posts skipped

Files created

Total media assets collected

Experts with inaccessible LinkedIn pages

Notes on missing data or scraping limitations