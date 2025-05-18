# Hacker News Daily Digest

This repository powers [hn.syazarilasyraf.com](https://hn.syazarilasyraf.com) — a daily digest of the top 10 Hacker News stories, generated automatically and published as a Jekyll blog.

## Features

- Fetches the top 10 HN stories every day  
- Auto-tags stories based on title, description, and URL domain  
- Generates a Markdown post with story links and “Save to Linkding” buttons  
- Sends a daily email digest via Buttondown  
- Archives past digests for easy browsing  
- Simple, mobile-friendly design with an index showing the latest digest only

## How it works

- A Python script fetches and filters HN stories using the official Firebase API  
- It applies custom tagging rules and generates a dated Markdown post under `_posts/`  
- The post is committed and deployed on GitHub Pages via GitHub Actions  
- Emails are sent automatically with the latest digest using Buttondown’s API

## Setup

1. Clone the repo  
2. Set environment variables:  
   - `LINKDING_URL` — your Linkding base URL (default: your personal Linkding)  
   - `BUTTONDOWN_API_KEY` — your Buttondown API key  
3. Configure GitHub Actions secrets accordingly  
4. Customize tags and synonyms in the Python script if desired  
5. Push changes and let the automation run daily

## Notes

- The “Save to Linkding” buttons add bookmarks to the configured Linkding account. Visitors wanting to save to their own Linkding should copy the story URL and title manually.  
- This is a personal project meant as a lightweight, no-backend Hacker News digest.

## License

MIT License © [Syazaril Asyraf](https://syazarilasyraf.com)