import requests
import datetime
import os
import pytz
import re

# Your tag list
TAGS = [
    "AI", "Browser", "Culture", "Database", "Design", "Developer", "Domain",
    "Financial", "Hacking", "Hardware", "History", "Humor", "Internet",
    "Marketing", "News", "Open-Source", "Personal", "Philosophy", "Practical",
    "Privacy", "Programming", "Project", "Projects", "Psychology", "Science",
    "Security", "Self", "Skills", "Social", "Software", "Tech", "Tools",
    "Travel", "Web", "Writing"
]

TAG_KEYWORDS = {tag.lower(): tag for tag in TAGS}

def get_hn_top_stories(limit=10):
    story_ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()
    top_stories = []
    for sid in story_ids[:limit * 3]:  # Fetch extra to filter bad ones
        story = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json").json()
        if story and 'title' in story and 'url' in story:
            top_stories.append(story)
        if len(top_stories) >= limit:
            break
    return top_stories

def auto_tag(title):
    tags = []
    title_words = re.findall(r'\w+', title.lower())
    for word in title_words:
        if word in TAG_KEYWORDS:
            tags.append(TAG_KEYWORDS[word])
    return sorted(set(tags))

def create_markdown_post(stories, date, linkding_url):
    filename = f"_posts/{date.strftime('%Y-%m-%d')}-hn.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"---\ntitle: \"Hacker News Digest – {date.strftime('%Y-%m-%d')}\"\ndate: {date.strftime('%Y-%m-%d')}\nlayout: post\n---\n\n")
        for i, s in enumerate(stories, 1):
            title = s.get("title")
            url = s.get("url")
            score = s.get("score", 0)
            comments = s.get("descendants", 0)
            tags = auto_tag(title)
            tag_str = ",".join(tags)
            encoded_url = requests.utils.quote(url, safe='')
            encoded_title = requests.utils.quote(title, safe='')
            save_url = f"{linkding_url}/bookmarks/new?url={encoded_url}&title={encoded_title}&tags={tag_str}"
            f.write(f"{i}. [{title}]({url}) — {score} points – {comments} comments  \n")
            f.write(f"   🔗 [Save to Linkding]({save_url})\n\n")

def main():
    # 7am Budapest time
    now = datetime.datetime.now(pytz.timezone("Europe/Budapest"))
    stories = get_hn_top_stories()
    linkding_url = os.getenv("LINKDING_URL", "https://bookmark.syazarilasyraf.com")
    create_markdown_post(stories, now, linkding_url)

if __name__ == "__main__":
    main()
