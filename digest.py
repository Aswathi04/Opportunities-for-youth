"""
Weekly digest: pulls new posts from Opportunities for Youth's RSS feed,
filters them to a keyword list of interest areas, skips ones already sent
before, and emails a clean HTML summary.

Honest limitations, read before relying on this:
- Keyword filtering is a blunt instrument. It will miss relevant posts that
  don't happen to use these exact words, and will occasionally include
  loosely-related ones that do. Treat the digest as a first pass, not a
  guarantee of completeness.
- OFY posts a wide mix of general scholarships/jobs/internships. Since this
  filters to a fairly specific interest area (policy, tech & society,
  inclusion, education), some weeks may have zero matches. That's expected,
  not a bug -- it means the source didn't post anything relevant that week.
- This only covers OFY. It intentionally does not pull from Google Alerts
  or other sources (per your choice) -- if you want broader coverage later,
  this script would need to loop over multiple feed URLs instead of one.
"""

import feedparser
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

FEED_URL = "https://opportunitiesforyouth.org/feed"
SEEN_FILE = Path(__file__).parent / "seen.json"

# Tune this list freely -- it's the single biggest lever on digest quality.
# Keep terms lowercase; matching is case-insensitive and just does a plain
# substring check against title + summary, so avoid overly short/common
# words (e.g. "ai" alone will false-positive on "aid", "aim", "faith" --
# hence the more specific phrasing choices below).
KEYWORDS = [
    "public policy", "policy fellowship", "policy analyst",
    "artificial intelligence", "ai governance", "ai policy",
    "digital rights", "internet freedom", "digital divide",
    "digital inclusion", "digital equity",
    "platform governance", "content moderation", "disinformation",
    "misinformation", "algorithmic accountability", "algorithmic bias",
    "civic tech", "govtech", "gov tech", "open government", "open data",
    "education policy", "edtech policy", "ed-tech policy",
    "tech and society", "technology and society", "responsible tech",
    "data governance", "internet governance",
]


def load_seen():
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text()))
    return set()


def save_seen(seen_ids):
    SEEN_FILE.write_text(json.dumps(sorted(seen_ids), indent=2))


def matches_keywords(entry):
    text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
    return [kw for kw in KEYWORDS if kw in text]


def build_email_html(matched_entries):
    if not matched_entries:
        return (
            "<p>No new posts matched your interest keywords this week. "
            "That's expected sometimes -- OFY posts a broad mix, and this "
            "filter is intentionally specific.</p>"
        )
    rows = []
    for entry, hits in matched_entries:
        title = entry.get("title", "(no title)")
        link = entry.get("link", "#")
        published = entry.get("published", "")
        summary = entry.get("summary", "")[:300]
        rows.append(f"""
        <div style="margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid #ddd;">
          <a href="{link}" style="font-size:16px;font-weight:bold;color:#1a0dab;text-decoration:none;">{title}</a>
          <div style="color:#666;font-size:12px;margin:4px 0;">{published} &middot; matched: {', '.join(hits)}</div>
          <div style="font-size:14px;color:#333;">{summary}...</div>
        </div>
        """)
    return "<h2>New opportunities this week</h2>" + "".join(rows)


def send_email(html_body):
    gmail_user = os.environ["GMAIL_USER"]
    gmail_app_password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ.get("DIGEST_TO", gmail_user)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your weekly Opportunities for Youth digest"
    msg["From"] = gmail_user
    msg["To"] = recipient
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_app_password)
        server.sendmail(gmail_user, recipient, msg.as_string())


def main():
    feed = feedparser.parse(FEED_URL)
    if feed.bozo:
        # The feed didn't parse cleanly. Don't silently send a broken/empty
        # digest -- fail loudly so you notice via the GitHub Actions run
        # status instead of just seeing "nothing new" every week.
        raise RuntimeError(f"Feed failed to parse: {feed.bozo_exception}")

    seen = load_seen()
    matched_entries = []
    new_seen = set(seen)

    for entry in feed.entries:
        entry_id = entry.get("id", entry.get("link"))
        if entry_id in seen:
            continue
        new_seen.add(entry_id)
        hits = matches_keywords(entry)
        if hits:
            matched_entries.append((entry, hits))

    html_body = build_email_html(matched_entries)
    send_email(html_body)
    save_seen(new_seen)

    print(f"Checked {len(feed.entries)} entries, {len(matched_entries)} matched, email sent.")


if __name__ == "__main__":
    main()
