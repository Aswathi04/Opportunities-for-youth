# OFY Weekly Digest

A weekly email digest of new posts from Opportunities for Youth, filtered
to your interest keywords (public policy, digital rights, platform
governance, civic tech, inclusion, education policy, etc.).

## Honest limitations, upfront

- **Keyword filtering is imprecise.** It's a plain substring match on title
  + summary. It will miss relevant posts that phrase things differently,
  and occasionally flag loosely-related ones. Check `digest.py`'s
  `KEYWORDS` list and tune it as you see real digests -- this is the
  single biggest lever on quality, and it's meant to be edited over time,
  not set once.
- **Some weeks will have zero matches.** OFY posts broadly (jobs,
  scholarships, general internships), and this filter is intentionally
  narrow to your specific interests. An empty digest most weeks means the
  filter is working as intended, not that something's broken.
- **This only covers OFY.** No other sources, per your choice earlier. If
  your interests broaden again, this script would need to loop over a list
  of feed URLs instead of a single one -- a moderate rewrite, not a
  one-line change.
- **RSS feed excerpts, not full articles.** The summary text is whatever
  OFY's feed includes -- usually a short excerpt, not the full post. You
  still click through to read details/deadlines.
- **Silent failure risk exists but is mitigated.** If the feed URL ever
  changes or breaks, the script raises an error rather than sending a
  broken digest -- check the "Actions" tab on GitHub occasionally for
  failed runs, since GitHub Actions won't proactively notify you by
  default unless you turn on failure-notification emails (see step 5).

## One-time setup

### 1. Create a GitHub repo
Create a new **private** repo (private matters here, since it'll hold your
email address in secrets -- though secrets themselves are encrypted
either way). Upload these files (`digest.py`, `requirements.txt`,
`seen.json`, and the `.github/workflows/weekly-digest.yml` folder)
keeping the same folder structure.

### 2. Create a Gmail App Password
Regular Gmail passwords won't work for this (Google blocks plain
password login from scripts). You need an "app password" instead:
1. Go to your Google Account -> Security -> 2-Step Verification (must be
   turned on first if it isn't already).
2. Search "App Passwords" in your account settings.
3. Generate one for "Mail" -- you'll get a 16-character code. Copy it,
   you won't be able to see it again.

### 3. Add secrets to your GitHub repo
In your repo: Settings -> Secrets and variables -> Actions -> New
repository secret. Add three:
- `GMAIL_USER` -- your Gmail address
- `GMAIL_APP_PASSWORD` -- the 16-character code from step 2
- `DIGEST_TO` -- the email address you want the digest sent to (can be
  the same Gmail address, or a different inbox entirely)

### 4. Test it manually before trusting the schedule
Go to the "Actions" tab in your repo -> "Weekly OFY Digest" ->
"Run workflow" (this works because of the `workflow_dispatch` trigger in
the yml). This runs it immediately instead of waiting for Monday, so you
can confirm the email actually arrives and looks right.

### 5. (Recommended) Turn on failure notifications
GitHub -> your profile picture -> Settings -> Notifications -> under
"Actions," make sure failed workflow email notifications are on. Without
this, a broken script fails silently in the Actions tab and you'd only
notice by checking manually.

## Tuning it over time
Edit the `KEYWORDS` list at the top of `digest.py` directly in GitHub
(or clone locally, edit, push) -- no need to touch the workflow file.
Commit the change and it takes effect on the next scheduled run.
