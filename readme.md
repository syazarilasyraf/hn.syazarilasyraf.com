# hn.syazarilasyraf.com

A minimal Hacker News daily digest. Every day at 7:00 AM, this site publishes the top 10 stories from Hacker News—complete with links, tags, and a one-click save button to [my Linkding instance](https://bookmark.syazarilasyraf.com).

Built with [Jekyll](https://jekyllrb.com), deployed via [Netlify](https://www.netlify.com/), and powered by a Python script scheduled with GitHub Actions.

**Live site:** [hn.syazarilasyraf.com](https://hn.syazarilasyraf.com)

---

## Features

- Automatically fetches the top 10 Hacker News stories daily
- Tags stories based on a custom keyword list
- One-click “Save to Linkding” button
- Auto-publishes to the site via Netlify
- Daily email digest sent with [Buttondown](https://buttondown.email/)
- Archives organized by date

---

## Workflow Overview

- At **7:00 AM (UTC+1)**, GitHub Actions runs `digest_script.py`
- The script:
  - Fetches current top stories from Hacker News
  - Creates a new Markdown post in `_posts/`
  - Commits the new file to the repository
- Netlify auto-builds the site with `bundle exec jekyll build`
- After the build, the script also sends the email digest via Buttondown

## Local Development

To run locally:

```bash
bundle install
bundle exec jekyll serve
```

To manually test the digest script:

```bash
python digest_script.py
```

> Make sure any required environment variables (API keys, tokens, etc.) are set locally.

---

## License

MIT
