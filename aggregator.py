import feedparser
import re
import os
import json
import hashlib
import firebase_admin
from firebase_admin import credentials, firestore

# Connect to Firebase securely using the GitHub Secret
cert_dict = json.loads(os.environ.get('FIREBASE_CREDENTIALS'))
cred = credentials.Certificate(cert_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()

SOURCES = [
    {"name": "Video Copilot", "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCw9S4RDEE7n71jY_RkY70Lw", "type": "tutorial"},
    {"name": "School of Motion", "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCz22I74rW2cwe-0bQ-O20YQ", "type": "tutorial"},
    {"name": "Lesterbanks", "url": "https://lesterbanks.com/feed/", "type": "inspiration"}
]

def fetch_and_upload():
    count = 0
    for source in SOURCES:
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries[:5]: # Grab latest 5
                
                thumbnail = ""
                if "media_thumbnail" in entry and len(entry.media_thumbnail) > 0:
                    thumbnail = entry.media_thumbnail[0]["url"]
                elif "media_content" in entry and len(entry.media_content) > 0:
                    thumbnail = entry.media_content[0]["url"]
                
                if not thumbnail:
                    html_text = entry.get("content", [{"value": ""}])[0].get("value", "") + entry.get("summary", "")
                    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html_text)
                    if img_match: thumbnail = img_match.group(1)
                        
                tags = [tag.term.lower() for tag in entry.get("tags", [])][:2] if "tags" in entry else ["after effects", "editing"]
                url = entry.get("link", "")
                
                item = {
                    "title": entry.get("title", ""),
                    "url": url,
                    "type": source["type"],
                    "tags": tags,
                    "thumbnail": thumbnail,
                    "source": source["name"],
                    "timestamp": firestore.SERVER_TIMESTAMP # Marks exact time added
                }
                
                # Create a safe, unique ID based on the URL to prevent duplicates
                doc_id = hashlib.md5(url.encode()).hexdigest()
                
                # Push to Firestore collection named 'content'
                db.collection('content').document(doc_id).set(item, merge=True)
                count += 1
        except Exception as e:
            print(f"Error fetching {source['name']}: {e}")
    return count

if __name__ == "__main__":
    print(f"Uploaded {fetch_and_upload()} items to Firebase!")
