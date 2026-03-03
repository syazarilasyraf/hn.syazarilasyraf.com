# Hacker News Digest

A minimal daily digest of top Hacker News stories.

**Live:** [hn.syazarilasyraf.com](https://hn.syazarilasyraf.com)

## Structure

- **/** — Live HN feed with real-time stories
- **/digest/** — Daily email digest archive
- **/archive/** — All past digests
- **/story/#{id}** — Full discussion threads

## Stack

- **Jekyll** — Static site generator
- **Python** — Daily digest script (`digest_script.py`)
- **GitHub Actions** — Scheduler
- **Netlify** — Hosting

## Local Development

```bash
bundle install
bundle exec jekyll serve
```

## Generate Digest

```bash
python digest_script.py --no-email
```

Options: `--limit`, `--timezone`, `--output-dir`

## License

MIT
