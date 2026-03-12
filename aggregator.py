import feedparser
import re
import os
import json
import hashlib
import firebase_admin
from firebase_admin import credentials, firestore

cert_dict = json.loads(os.environ.get('FIREBASE_CREDENTIALS'))
cred = credentials.Certificate(cert_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()

SOURCES = [
    {"name": "Video Copilot", "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCw9S4RDEE7n71jY_RkY70Lw", "type": "tutorials"},
    {"name": "School of Motion", "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCz22I74rW2cwe-0bQ-O20YQ", "type": "tutorials"},
    {"name": "Film Riot", "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UC6P24bhhCmMqcC07VeqJZqw", "type": "tutorials"}
]

# The Auto-Tagging Engine
TAG_KEYWORDS = {
    "after effects": "after effects", "ae": "after effects",
    "premiere": "premiere pro", "pr": "premiere pro",
    "resolve": "davinci resolve", "davinci": "davinci resolve",
    "capcut": "capcut", "alight motion": "alight motion",
    "typography": "typography", "vfx": "vfx & compositing",
    "color grading": "color grading", "amv": "fan edits",
    "speed ramp": "speed ramping", "twixtor": "twixtor",
    "sapphire": "sapphire", "element 3d": "element 3d",
    "free": "assets", "preset": "assets", "overlay": "assets"
}

def fetch_and_upload():
    count = 0
    for source in SOURCES:
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries[:5]:
                thumbnail = ""
                if "media_thumbnail" in entry and len(entry.media_thumbnail) > 0:
                    thumbnail = entry.media_thumbnail[0]["url"]
                elif "media_content" in entry and len(entry.media_content) > 0:
                    thumbnail = entry.media_content[0]["url"]
                
                html_text = entry.get("content", [{"value": ""}])[0].get("value", "") + entry.get("summary", "")
                if not thumbnail:
                    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html_text)
                    if img_match: thumbnail = img_match.group(1)
                
                title = entry.get("title", "")
                text_to_scan = (title + " " + html_text).lower()
                
                # Assign tags based on keywords found in the post
                tags = set([source["type"]]) # Base tag
                for keyword, tag in TAG_KEYWORDS.items():
                    if keyword in text_to_scan:
                        tags.add(tag)
                
                url = entry.get("link", "")
                item = {
                    "title": title,
                    "url": url,
                    "type": source["type"],
                    "tags": list(tags)[:4], # Limit to max 4 tags
                    "thumbnail": thumbnail,
                    "source": source["name"],
                    "timestamp": firestore.SERVER_TIMESTAMP
                }
                
                doc_id = hashlib.md5(url.encode()).hexdigest()
                db.collection('content').document(doc_id).set(item, merge=True)
                count += 1
        except Exception as e:
            print(f"Error fetching {source['name']}: {e}")
    return count

if __name__ == "__main__":
    print(f"Uploaded {fetch_and_upload()} items to Firebase!")
