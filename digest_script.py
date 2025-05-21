import requests
import datetime
import os
import pytz
from urllib.parse import urlparse

HN_ITEM_URL = "https://news.ycombinator.com/item?id="

def get_hn_top_stories(limit=10):
    story_ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()
    top_stories = []
    for sid in story_ids[:limit * 3]:  # Fetch more to filter
        story = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json").json()
        if story and 'title' in story and 'url' in story:
            top_stories.append(story)
        if len(top_stories) >= limit:
            break
    return top_stories

def create_markdown_post(stories, date, linkding_url):
    os.makedirs("_posts", exist_ok=True)
    filename = f"_posts/{date.strftime('%Y-%m-%d')}-hn.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(
            f"---\n"
            f"title: \"Hacker News Digest · “ {date.strftime('%B %d, %Y')}\"\n"
            f"date: {date.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
            f"layout: post\n"
            f"---\n\n"
        )
        f.write(f"*Top stories as of {date.astimezone(pytz.utc).strftime('%H:%M')} UTC*\n\n")
        for i, s in enumerate(stories, 1):
            title = s.get("title")
            url = s.get("url")
            score = s.get("score", 0)
            comments = s.get("descendants", 0)
            hn_link = f"{HN_ITEM_URL}{s['id']}"
            encoded_url = requests.utils.quote(url, safe='')
            encoded_title = requests.utils.quote(title, safe='')
            save_url = f"{linkding_url}/bookmarks/new?url={encoded_url}&title={encoded_title}"
            f.write(f"{i}. [{title}]({url}) · ” {score} points, [{comments} comments]({hn_link})  \n")
            f.write(f"   🔗 · [Save]({save_url})\n\n")

        f.write(f"\n_Last updated: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}_\n")

def format_email_body(stories, date, linkding_url):
    lines = [f"*Top stories as of {date.astimezone(pytz.utc).strftime('%H:%M')} UTC*\n"]
    for i, s in enumerate(stories, 1):
        title = s.get("title")
        url = s.get("url")
        score = s.get("score", 0)
        comments = s.get("descendants", 0)
        hn_link = f"{HN_ITEM_URL}{s['id']}"
        encoded_url = requests.utils.quote(url, safe='')
        encoded_title = requests.utils.quote(title, safe='')
        save_url = f"{linkding_url}/bookmarks/new?url={encoded_url}&title={encoded_title}"
        line = f"{i}. [{title}]({url}) · ” {score} points, [{comments} comments]({hn_link})"
        line += f"\n   🔗 · [Save]({save_url})\n"
        lines.append(line)
    return "\n".join(lines)

def send_to_buttondown(subject, body, api_key):
    response = requests.post(
        "https://api.buttondown.email/v1/emails",
        headers={"Authorization": f"Token {api_key}"},
        json={
            "subject": subject,
            "body": body,
            "publish": True
        }
    )
    if response.status_code == 201:
        print("✅ Email sent successfully to Buttondown")
    else:
        print( f"❌ Failed to send email: {response.status_code} {response.text}")

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    tz = pytz.timezone("Europe/Budapest")
    now = datetime.datetime.now(tz).replace(minute=0, second=0, microsecond=0)
    stories = get_hn_top_stories()
    linkding_url = os.getenv("LINKDING_URL", "https://bookmark.syazarilasyraf.com")
    buttondown_api_key = os.getenv("BUTTONDOWN_API_KEY")

    create_markdown_post(stories, now, linkding_url)

    subject = f"Hacker News Digest · “ {now.strftime('%B %d, %Y')}"
    body = format_email_body(stories, now, linkding_url)
    send_to_buttondown(subject, body, buttondown_api_key)

if __name__ == "__main__":
    main()
