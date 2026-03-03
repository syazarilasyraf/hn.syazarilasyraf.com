import requests
import datetime
import os
import pytz
from urllib.parse import urlparse
import logging
import sys
import time
import argparse
import yaml

HN_ITEM_URL = "https://news.ycombinator.com/item?id="

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


def get_hn_top_stories(limit=10):
    try:
        story_ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        story_ids.raise_for_status()
        story_ids = story_ids.json()
    except Exception as e:
        logging.error(f"Failed to fetch top stories: {e}")
        return []
    top_stories = []
    for sid in story_ids[:limit * 3]:
        try:
            story = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=10)
            story.raise_for_status()
            story = story.json()
        except Exception as e:
            logging.warning(f"Failed to fetch story {sid}: {e}")
            continue
        if story and 'title' in story and 'url' in story:
            top_stories.append(story)
        if len(top_stories) >= limit:
            break
        time.sleep(0.1)  # Be nice to the API
    return top_stories


def get_domain(url):
    return urlparse(url).netloc.replace("www.", "")


def create_markdown_post(stories, date, output_dir, data_dir="_data"):
    try:
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)
        
        # Get both local and UTC dates for filenames
        # Jekyll may interpret the date differently based on timezone
        local_date_str = date.strftime('%Y-%m-%d')
        utc_date = date.astimezone(pytz.utc)
        utc_date_str = utc_date.strftime('%Y-%m-%d')
        
        filename = f"{output_dir}/{local_date_str}-hn.md"
        
        # Create data file with local date (matches post filename)
        data_filename = f"{data_dir}/{local_date_str}-hn.yml"
        
        # Prepare story data for YAML
        stories_data = []
        for s in stories:
            stories_data.append({
                'id': s['id'],
                'title': s.get('title'),
                'url': s.get('url'),
                'domain': get_domain(s.get('url', '')),
                'comments': s.get('descendants', 0),
                'score': s.get('score', 0),
                'by': s.get('by', 'unknown'),
                'hn_url': f"{HN_ITEM_URL}{s['id']}"
            })
        
        # Write YAML data file for structured access
        with open(data_filename, 'w', encoding='utf-8') as f:
            yaml.dump({
                'date': date.strftime('%Y-%m-%d'),
                'stories': stories_data
            }, f, default_flow_style=False, allow_unicode=True)
        logging.info(f"Data file created: {data_filename}")
        
        # Also create UTC date version if different (for timezone compatibility)
        if utc_date_str != local_date_str:
            utc_data_filename = f"{data_dir}/{utc_date_str}-hn.yml"
            with open(utc_data_filename, 'w', encoding='utf-8') as f:
                yaml.dump({
                    'date': utc_date_str,
                    'stories': stories_data
                }, f, default_flow_style=False, allow_unicode=True)
            logging.info(f"Data file created: {utc_data_filename}")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(
                f"---\n"
                f"title: \"Hacker News Digest · {date.strftime('%B %d, %Y')}\"\n"
                f"date: {date.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
                f"layout: post\n"
                f"---\n\n"
            )
            for s in stories:
                title = s.get("title")
                url = s.get("url")
                comments = s.get("descendants", 0)
                hn_link = f"{HN_ITEM_URL}{s['id']}"
                domain = get_domain(url)
                story_id = s['id']

                f.write(f"[{title}]({url})  ")
                f.write(f"{domain} / [{comments} comments]({hn_link})\n\n")

            f.write(f"\n_Last updated: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}_\n")
        logging.info(f"Markdown post created: {filename}")
    except Exception as e:
        logging.error(f"Failed to create markdown post: {e}")


def format_email_body(stories, date):
    lines = [f"<p><em>Top stories as of {date.astimezone(pytz.utc).strftime('%H:%M')} UTC</em></p>"]
    for s in stories:
        title = s.get("title")
        url = s.get("url")
        comments = s.get("descendants", 0)
        story_id = s['id']
        # Link to your site's story page instead of HN
        site_comment_link = f"https://hn.syazarilasyraf.com/story/#{story_id}"
        hn_link = f"{HN_ITEM_URL}{story_id}"
        domain = get_domain(url)

        lines.append(
            f"<p>"
            f"<strong><a href=\"{url}\">{title}</a></strong><br>"
            f"<span style=\"color:#888;font-size:0.9em\">{domain}</span> / "
            f"<a href=\"{site_comment_link}\" style=\"font-size:0.9em;text-decoration:none;color:inherit\">{comments} comments</a>"
            f"</p>"
        )
    return "\n".join(lines)


def send_to_buttondown(subject, body, api_key):
    if not api_key:
        logging.error("BUTTONDOWN_API_KEY is not set. Email will not be sent.")
        return
    try:
        response = requests.post(
            "https://api.buttondown.email/v1/emails",
            headers={"Authorization": f"Token {api_key}"},
            json={
                "subject": subject,
                "body": body,
                "publish": True
            },
            timeout=15
        )
        if response.status_code == 201:
            logging.info("Email sent successfully to Buttondown")
        else:
            logging.error(f"Failed to send email: {response.status_code} {response.text}")
    except Exception as e:
        logging.error(f"Exception while sending email: {e}")


def main():
    parser = argparse.ArgumentParser(description="Generate and send a Hacker News digest.")
    parser.add_argument('--limit', type=int, default=10, help='Number of top stories to fetch (default: 10)')
    parser.add_argument('--timezone', type=str, default='Europe/Budapest', help='Timezone for the digest (default: Europe/Budapest)')
    parser.add_argument('--output-dir', type=str, default='_posts', help='Directory to save the markdown post (default: _posts)')
    parser.add_argument('--no-email', action='store_true', help='Do not send the email newsletter')
    args = parser.parse_args()

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    try:
        tz = pytz.timezone(args.timezone)
    except Exception as e:
        logging.error(f"Invalid timezone '{args.timezone}': {e}")
        sys.exit(1)
    now = datetime.datetime.now(tz).replace(minute=0, second=0, microsecond=0)
    stories = get_hn_top_stories(limit=args.limit)
    buttondown_api_key = os.getenv("BUTTONDOWN_API_KEY")

    create_markdown_post(stories, now, args.output_dir, "_data")

    if not args.no_email:
        if not buttondown_api_key:
            logging.error("BUTTONDOWN_API_KEY environment variable is missing. Exiting.")
            sys.exit(1)
        subject = f"Hacker News Digest · {now.strftime('%B %d, %Y')}"
        body = format_email_body(stories, now)
        send_to_buttondown(subject, body, buttondown_api_key)
    else:
        logging.info("Email sending skipped due to --no-email flag.")


if __name__ == "__main__":
    main()
