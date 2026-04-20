# Expert Name: Edward Sturm
# Video Title: Deindexed Overnight: The SEO Nightmare That Wasn’t What It Seemed
# Video URL: https://www.youtube.com/watch?v=nyT2L8m6Aco
# Publish Date: 2026-04-16
# Created Date: 2026-04-16

# Video Statistics (if available):
- Views: 2,879
- Likes: 115
- Comments: 31
- Duration: 16:49

# Transcript Source: Supadata

## Transcript

This is an insane realworld SEO case
study where a site was completely
removed from Google's index overnight,
completely removed. The situation
started with a simple email. We are not
in Google's index. And what followed was
a full investigation into what caused
the de-indexing, how it was diagnosed,
and how the site ultimately recovered.
This is a great great write up by Mr.
Glenn Gabe. You're going to like it. I
read it last night. I said, "This is
amazing." So, it starts, "Wednesday was
a relatively normal day for me in
Googleland. I was auditing client sites,
still digging into the March 2026 core
update movement, and posting the latest
SEO and AI search news across social
media. But then an interesting email
arrived. It was from a company I helped
last year, and the subject line said it
all. We are not in Google's index."
Well, that caught my attention. It's a
company in a YML niche that has been
impacted by several major updates in the
past, but has worked hard to improve
over time. YM means, if you don't know,
it means your money, your life. So, this
is health, this is finance. These are
niches where the information that
somebody gets will directly impact their
wallet or their body. And Google has
tighter algorithms, stricter algorithms
for niches in YM L. Google is less
tolerant of spam signals and requires
even more authority, topical authority.
So like a link from you know a
healthline or something or a.gov site or
aedu Glen Gabe continues also they have
been doing quite well in Google Wise
over the past 6 months while they
continue to work on improving quality
across the site content user experience
technical SEO etc. The site has a
footprint of about 20,000 URLs. So, it's
not a huge site, but it's not small
either. I can't go into too much detail
about their focus or content, but there
is a programmatic aspect to the site. In
addition, I covered an important topic
with them during the audit last year,
which was AI generated content. There
are pockets of AI generated content
across a number of pages on the site and
it definitely concerned me. And if you
follow me on social media or read my
blog, you know I am not a fan of sites
publishing 100% AI generated content and
especially for your money your life
content. I coined the term mount AI and
for a good reason. I actually didn't
even know that Glen Gabe came up with
Mount AI and I've been talking about it
a lot and it's what you see with scaled
AI generated content and you see tons of
rankings coming in really fast, traffic
increasing super super fast. Google
picking up on the signals for organic
traffic, increasing so much rankings,
increasing so much other signals that
there are with with pushing out mass
amounts of AI generated content and
ultimately you see sites getting hit and
then it just spikes down and it looks
like a mountain. So that's what Glen
Gabe thought this might be. Is that the
case? Let's continue. Glenn says, "To
clarify, the entire pages aren't AI
generated, but some sections were. The
AI content isn't spammy or egregious,
nor was it there to game Google's
algorithm, but there was quite a bit of
it when I audited the site last year.
After the audit, they have been working
to address that situation by publishing
more human content, but it's taking time
to address across the entire site. And
again, there was always human content,
but just sections of AI generated
content mixed in. Back to that email. As
you can guess, with an emergency email
arriving about being de-indexed, my
first thought went straight to AI and
programmatic content. But as with any
good mystery, things may not be what
they seem in the early stages of the
story. In this post, I'll cover what
took place, how I troubleshooted the
situation, what my client found, and how
the situation ended up. Also, I want to
thank my client for letting me publish
this case study. I think it could help
other site owners that might find
themselves in a similar situation. It
was an interesting one, that's for sure.
Let's get started. And it really could.
When I read this, I said, "Oh, yeah.
This could definitely help other
people." So, the email, help, we've been
completely de-indexed. After receiving
the email, I immediately ran a quick
site query. Yep, the site was completely
de-indexed. That's a big hammer for
Google. So, something was clearly not
right. They were nuked from the SERs.
Proof gone. And so he he just put the
their homepage he put site colon and
their homepage into Google and Google
showed absolutely nothing except for try
Google search console if you own this
site. Glenn continues next I jumped into
Google search console to check for
manual actions or security issues. There
was not a manual action yet and the
security viewer was clear as well. Note
that does not mean the site didn't have
a manual action. Manual actions can be
delayed and I explained that to my
client. And without a manual action, you
must put your SEO detective hat on and
start investigating the situation.
That's where things got interesting.
Based on what I explained before, my
first thought was the AI generated
content since it was across a number of
pages on the site. It wasn't the full
content of the page, but there was a lot
of it in sections within pages. So, was
this a manual action for scaled content
abuse, or was there something else at
play? I immediately dug into Google
Search Console to see what I could find.
There were properties set up for the
core URL prefix versions of the site.
HTTPS, nonWW property, a domain
property, and then some directory
properties. And I share in compact
keywords that you should add all
prefixes to Google search console. And
what follows is a good example of why
you should do that. Compact keywords is
the thing on my shirt. It's my SEO
course. And I get emails. I used to get
emails. I put in a reason into the
course explaining why you should do
this. Before that, I used to get emails
like, "Why should we add all these
domain variations?" And this is a
perfect example of why you should. So,
Glenn continues, "But one important
property was missing, and it's one I
always recommend setting up. That's the
HTTPS www property, even if a site isn't
using that version. I'll come back to
this important finding soon." So, for
example, if you're using https but no
www, you just go straight to the domain
name. You should still have the www
monitored in your Google search console.
Glenn says when digging in the core URL
prefix property for the site, https
nonwww
look totally normal in the performance
reporting. Clicks and impressions were
chugging along as usual with a decent
increase based on the March 2026 core
update. Again, they have been working
hard to improve over time. But then I
started digging into the other
properties and it didn't take long to
find something that looked very off.
When checking the domain property, which
covers all protocols and subdomains, I
noticed a huge spike in impressions and
clicks on one specific day. Filtering by
page revealed it was the homepage of the
non-cononical version of the site,
httpsswwww.
It oddly spiked like crazy on one day.
The site jumped to nearly 12,000 clicks
per day out of the blue. And checking
the queries that page ranked for yielded
a critical problem. Here it comes. All
of the queries were gambling related.
Yep, the site was hacked. And it was
just the www version of the homepage
that was hacked, which was redirecting
to some gambling site. And since my
client was just checking the canonical
version of the site, https nonwww,
they didn't even realize this happened.
The domain property revealed the
problem, but they weren't checking that
property. Also, having the https www
version setup would have revealed the
issue as well, but that wasn't even set
up. Here are the gambling queries when
you isolated the www homepage. The
visibility tools picked this up as well,
and you could see the various SER
screenshots that were captured during
the hack showing the www homepage with a
new favicon title and snippet. And
again, when you click through, the
hacked page redirected users downstream
to a gambling site. Remember, this was a
site covering a your money, your life
topic. Oof. I immediately emailed my
clients explaining they were hacked and
included all of the screenshots. They
moved quickly to clean up the problem
and close the security hole. I'll cover
what that security vulnerability was
soon, but they cleaned everything up
very quickly within an hour or so, but
they were still de-indexed and were
confused about the next steps. When I
got to this part of the story, when I
was reading this last night, I was on
the I'm not going to lie, I was on the
edge of my seat of like, oh my gosh, can
they can can they recover? Can they fix
this? How how are they going to how are
they going to move forward with this?
How long is it going to take? They
didn't even get a manual action yet.
Glenn continues, "I told my client when
they first emailed me that a manual
action was probably on its way, and I
was right." There we go. The next
morning, 3:00 a.m. Eastern time to be
specific, the manual action arrived, and
it was for quote unquote major spam
problems impacting the entire site.
interesting that Google used quote
unquote major spam problems and that it
impacted the entire site since it was
only the homepage of the www subdomain.
But regardless, the entire site was
impacted. In Google's notice, it says,
"Fix this problem now. Update your pages
to meet Google spam policies and then
submit a reconsideration request." This
is the exact message that Google gave
along with major spam problems. The
description is pages on this site appear
to use aggressive spam techniques such
as scaled content abuse, cloaking,
scraping content from other websites
and/or repeated or egregious violations
of Google's spam policies for web
search. And Google says affects all
pages. So, if the digging hadn't been
done, this message wouldn't have made it
clear what the problem was. Like Glenn
wrote, it was only the homepage of the
www subdomain, but the entire site was
impacted. So, here we go. My client
immediately filled a reconsideration
request explaining that they were
hacked, that they cleaned up the
situation, etc. Now, they just needed to
wait for Google to review the request. I
was hoping that would happen quickly,
but you never know. This is was really
like, oh my gosh, like they could wait a
month, they could wait a week, they
could wait not long at all, they could
wait 3 months, they they could wait a
year. What's going to happen? And Glenn
says, but quick it was. The next
morning, I noticed all of the pages were
showing back up in the SERs via site
query, even though my client hadn't
received a message back from Google yet
about the reconsideration request. I
notified my client immediately, and they
were thrilled to see the site back
ranking where it should be. And then the
message from Google finally showed up a
few hours later in Google Search Console
and via email. The reconsideration
request was approved and the manual
action lifted. and you see that message
in Google search console reconsideration
requests approved for the site. So this
next part is about the security hole and
how to avoid things like this if you
want if you're concerned that this could
happen to you. So Glenn wrote, "Once I
sent the information through about the
www version of the homepage getting
hacked, the technical lead for my client
moved quickly to rectify the situation."
He also explained how this happened via
email. I'll provide the details below. I
hope this can help some site owners out
there that might have a similar setup.
I.e. the following bullets could help
you avoid opening a security hole or if
you get hacked, how to close a security
hole quickly. So, here are the bullets.
Nothing on our site uses www and we had
redirect rules driving all requests to
nonwww.
And all of our site monitoring was
pointing at nonwww
versions of our site. That was a
mistake. Our wwwns
entry pointed to an old Azure web app
that helped with the redirects among
other things. We forgot about this www
entry and decommissioned the old web
app. As soon as Azure released the web
app name and corresponding DNS entry,
someone else grabbed it and pointed it
at their spam site. I'm kind of amazed
Azure allowed something so sketchy to
run on their platform, but this is
undoubtedly harder to monitor than you'd
think. So no warnings or flags were
triggered and we didn't even think to
look at the www. It was easy to go fix
the www DNS entry but then it takes a
bit of time to have DNS propagate and
then Google to see that the problem had
been rectified. So if your site is
resolving as nonwww then make sure you
know how www is being handled. Don't
just monitor the nonwww version make
sure you monitor www as well. If not,
someone could eventually hack it, take
control, redirect users to any site they
want, including spammy or dangerous
sites. And the manual action lagged a
bit, so there was about a day of stress
while figuring this all out. Then they
filed a reconsideration request, and the
action was lifted the following day.
I'll end with some final bullets for
site owners based on this situation.
Make sure to set up all versions of your
site in Google Search Console as
properties. that includes a domain
property https www h h h h h h h h h h h
h h h h h h h h h h h h h h h h h h h h
h h h h h h h h h n n n n n n n n n n n
n n n n n n n n non www, http www, http
nonwww
important directories, etc. All versions
monitor all versions of your site from a
security and performance perspective. If
your site only resolves at www or
nonwww, make sure you are monitoring the
other version. Ensure DNS is handled
properly for your site. As this case
demonstrated, what seems like one minor
change yielded an opportunity for
hackers to take control of the www
version of the homepage. Then all hell
broke loose. Manual actions can take
time to show up in search console, even
when the site is already being impacted
in the search results. So there's a lag
that can be confusing for site owners.
Just understand this can happen as you
dig into the situation. Also, don't make
any rash decisions until you know what
the manual action is for and that you
definitely have a manual action. When
investigating the problem, dig into each
Google Search Console property and look
for strange surges or drops. In this
situation, the HTTPS www version of the
homepage surged like crazy. Isolating
that page and viewing the queries
yielded the problem. Slice and dice your
Google Search Console reporting. You can
often find the culprit. Although AI
generated content wasn't the cause of
this manual action, you should still be
very careful with how you utilize AI
content and scale it. Do not just scale
100% AI generated content and think that
will be okay over the long term. I have
covered what I call mount AI many times
across social media. Beware. And this
amazing blog post wraps up. Glenn says,
"That was a pretty stressful few days
for my client, and I appreciate them
letting me write this post again. I hope
it can help some site owners out there
that might run into the same type of
vulnerability with their own sites. This
case demonstrates how one page getting
hacked led to an entire site getting
flagged as spam. Then they were
de-indexed and removed from the search
results. To add insult to injury, manual
actions can often show up down the line
after the site is impacted in the search
results. So, make sure you stay on top
of site security. Then you can hopefully
avoid a situation like this. The good
news is that my client is back in the
index. The manual auction is removed.
They are ranking where they were and
their business is humming again. Oh, and
you better believe they are now
monitoring the www version of this site.
And we get a very happy ending from Mr.
Glen Gabe. Thank you to Glen Gabe for
writing that. Thank you to Gog and Gotra
for sending me that. And thank you for
watching this episode. If you watch this
on YouTube or listening if you listened
on Spotify or Apple Podcast, this is
episode 1 of the Edward Show. This is my
daily digital marketing podcast 1 days
in a row doing this show. If you want to
see me doing search engine optimization,
sharing my screen, showing how I find
keywords, showing how I do link
building, showing how I do a technical
audit, a site audit, showing how I make
bottom offunnel conversion-based SEO
landing pages, showing how I structure
my sites for these landing pages and so
much more. That is my SEO course,
compact keywords.com. If you haven't
checked it out yet, you are going to
love it. And that is all for the show.
Thank you, thank you, thank you for
watching and listening. And I will talk
to you again tomorrow.
