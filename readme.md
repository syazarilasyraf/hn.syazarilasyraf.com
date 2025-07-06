# hn.syazarilasyraf.com

A minimal Hacker News daily digest. Every day at 7:00 AM, this site publishes the top 10 stories from Hacker News—complete with links, ~~and a one-click save button to [my Linkding instance](https://bookmark.syazarilasyraf.com).~~

Built with [Jekyll](https://jekyllrb.com), deployed via [Netlify](https://www.netlify.com/), and powered by a Python script scheduled with GitHub Actions.

**Live site:** [hn.syazarilasyraf.com](https://hn.syazarilasyraf.com)

---

## Features

- Automatically fetches the top 10 Hacker News stories daily
- Auto-publishes to the site via Netlify
- Daily email digest sent with [Buttondown](https://buttondown.email/)
- Archives organized by date
- Easily configurable via command-line arguments

---

## Workflow Overview

- At **7:00 AM (UTC+1)**, GitHub Actions runs `digest_script.py`
- The script:
  - Fetches current top stories from Hacker News
  - Creates a new Markdown post in the specified output directory (default: `_posts/`)
  - Commits the new file to the repository
  - Optionally sends the daily email digest via Buttondown (can be disabled)
- Netlify auto-builds the site with `bundle exec jekyll build`

## Local Development

To run locally:

```bash
bundle install
bundle exec jekyll serve
```

To manually test the digest script with custom options:

```bash
python digest_script.py --limit 5 --timezone "Asia/Kuala_Lumpur" --output-dir "my_posts" --no-email
```

**Available options:**
- `--limit` (number of top stories, default: 10)
- `--timezone` (timezone for the digest, default: Europe/Budapest)
- `--output-dir` (directory for markdown post, default: _posts)
- `--no-email` (skip sending the email newsletter)

> Make sure any required environment variables (API keys, tokens, etc.) are set locally.

---

## License

MIT SyazarilAsyraf
