import requests
import datetime
import os
import pytz
import re
from urllib.parse import urlparse

# Configuration
TAGS = [
    "AI", "Browser", "Culture", "Database", "Design", "Developer", "Domain",
    "Financial", "Hacking", "Hardware", "History", "Humor", "Internet",
    "Marketing", "News", "Open-Source", "Personal", "Philosophy", "Practical",
    "Privacy", "Programming", "Project", "Projects", "Psychology", "Science",
    "Security", "Self", "Skills", "Social", "Software", "Tech", "Tools",
    "Travel", "Web", "Writing"
]

# Synonym dictionary: key words (lowercase) to tags
SYNONYMS = {
    "ai": "AI",
    "machine learning": "AI",
    "ml": "AI",
    "database": "Database",
    "sql": "Database",
    "nosql": "Database",
    "javascript": "Programming",
    "python": "Programming",
    "developer": "Developer",
    "dev": "Developer",
    "privacy": "Privacy",
    "security": "Security",
    "hacking": "Hacking",
    "open source": "Open-Source",
    "opensource": "Open-Source",
    "marketing": "Marketing",
    "travel": "Travel",
    "hardware": "Hardware",
    "design": "Design",
    "web": "Web",
    "browser": "Browser",
    "science": "Science",
    "philosophy": "Philosophy",
    "psychology": "Psychology",
    "social": "Social",
    "tools": "Tools",
    "writing": "Writing",
    # Add more synonyms here as needed
}

# Domain to tags mapping
DOMAIN_TAGS = {
    # Popular Dev & Open-Source
    "github.com": "Open-Source",
    "gitlab.com": "Open-Source",
    "stackoverflow.com": "Developer",
    "npmjs.com": "Tools",
    "dev.to": "Developer",
    "medium.com": "Writing",
    "hashnode.com": "Developer",

    # News & Tech Media
    "techcrunch.com": "Tech",
    "theverge.com": "Tech",
    "wired.com": "Tech",
    "arstechnica.com": "Tech",
    "thenextweb.com": "Tech",

    # Cloud Providers & Infrastructure
    "aws.amazon.com": "Cloud",
    "cloud.google.com": "Cloud",
    "azure.microsoft.com": "Cloud",
    "digitalocean.com": "Cloud",

    # AI, Data Science, Research
    "arxiv.org": "Science",
    "kaggle.com": "Data",
    "towardsdatascience.com": "AI",
    "paperswithcode.com": "AI",

    # Security & Privacy
    "securityweekly.com": "Security",
    "mitre.org": "Security",
    "cvedetails.com": "Security",
    "haveibeenpwned.com": "Security",

    # Social & Community
    "reddit.com": "Social",
    "twitter.com": "Social",
    "hackernews.com": "News",
    "lobsters.org": "Social",

    # Business & Startups
    "techstars.com": "Startup",
    "ycombinator.com": "Startup",
    "crunchbase.com": "Startup",

    # Misc
    "youtube.com": "Culture",
    "imgur.com": "Culture",
    "spotify.com": "Culture",
    "patreon.com": "Personal",
}

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

def auto_tag(title, url, description=None):
    tags = set()
    combined_text = title.lower()
    if description:
        combined_text += " " + description.lower()
    
    # Check synonyms
    for key, tag in SYNONYMS.items():
        if key in combined_text:
            tags.add(tag)

    # Check domain
    domain = urlparse(url).netloc.lower()
    for d, tag in DOMAIN_TAGS.items():
        if domain == d or domain.endswith("." + d):
            return tag
    
    # No default fallback tag
    
    return sorted(tags)

def create_markdown_post(stories, date, linkding_url):
    os.makedirs("_posts", exist_ok=True)
    filename = f"_posts/{date.strftime('%Y-%m-%d')}-hn.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(
            f"---\n"
            f"title: \"Hacker News Digest – {date.strftime('%B %d, %Y')}\"\n"
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
            description = s.get("text", "")
            tags = auto_tag(title, url, description=description)
            tag_str = ",".join(tags)
            encoded_url = requests.utils.quote(url, safe='')
            encoded_title = requests.utils.quote(title, safe='')
            save_url = f"{linkding_url}/bookmarks/new?url={encoded_url}&title={encoded_title}&tags={tag_str}"
            f.write(f"{i}. [{title}]({url}) — {score} points, [{comments} comments]({hn_link})  \n")
            if tags:
                f.write(f"   🏷️ Tags: {tag_str}\n")
            f.write(f"   🔗 [Save to Linkding]({save_url})\n\n")

        f.write(f"\n_Last updated: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}_\n")

    filesize = os.path.getsize(filename)
    print(f"✅ Created markdown post: {filename} ({filesize} bytes)")
    print("🔍 Directory contents after post creation:")
    print(os.listdir("_posts"))

def format_email_body(stories, date, linkding_url):
    lines = [f"*Top stories as of {date.astimezone(pytz.utc).strftime('%H:%M')} UTC*\n"]
    for i, s in enumerate(stories, 1):
        title = s.get("title")
        url = s.get("url")
        score = s.get("score", 0)
        comments = s.get("descendants", 0)
        hn_link = f"{HN_ITEM_URL}{s['id']}"
        description = s.get("text", "")
        tags = auto_tag(title, url, description=description)
        tag_str = ",".join(tags)
        encoded_url = requests.utils.quote(url, safe='')
        encoded_title = requests.utils.quote(title, safe='')
        save_url = f"{linkding_url}/bookmarks/new?url={encoded_url}&title={encoded_title}&tags={tag_str}"
        line = f"{i}. [{title}]({url}) — {score} points, [{comments} comments]({hn_link})"
        if tags:
            line += f"\n   🏷️ Tags: {tag_str}"
        line += f"\n   🔗 [Save to Linkding]({save_url})\n"
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
        print(f"❌ Failed to send email: {response.status_code} {response.text}")

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    tz = pytz.timezone("Europe/Budapest")
    now = datetime.datetime.now(tz).replace(minute=0, second=0, microsecond=0)
    stories = get_hn_top_stories()
    linkding_url = os.getenv("LINKDING_URL", "https://bookmark.syazarilasyraf.com")
    buttondown_api_key = os.getenv("BUTTONDOWN_API_KEY")

    create_markdown_post(stories, now, linkding_url)

    subject = f"Hacker News Digest – {now.strftime('%B %d, %Y')}"
    body = format_email_body(stories, now, linkding_url)
    send_to_buttondown(subject, body, buttondown_api_key)

if __name__ == "__main__":
    main()