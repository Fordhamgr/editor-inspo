import feedparser
import json
from datetime import datetime

# Feeds tailored for video editors
SOURCES = [
    {"name": "School of Motion", "url": "https://www.schoolofmotion.com/blog/rss.xml", "type": "tutorial"},
    {"name": "Lesterbanks", "url": "https://lesterbanks.com/feed/", "type": "inspiration"},
    {"name": "YouTube (Example)", "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UC...YOUR_ID_HERE", "type": "tutorial"}
]

def fetch_content():
    items = []
    for source in SOURCES:
        feed = feedparser.parse(source["url"])
        for entry in feed.entries[:5]:  # Grab the latest 5 posts per source
            
            # Safely extract a thumbnail if it exists
            thumbnail = ""
            if "media_thumbnail" in entry and len(entry.media_thumbnail) > 0:
                thumbnail = entry.media_thumbnail[0].get("url", "")
                
            item = {
                "id": entry.get("id", entry.get("link", "")),
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "type": source["type"],
                "tags": [tag.term.lower() for tag in entry.get("tags", [])][:3], # Grab up to 3 tags
                "thumbnail": thumbnail,
                "source": source["name"],
                "published": entry.get("published", "")
            }
            items.append(item)
    return items

if __name__ == "__main__":
    new_items = fetch_content()
    
    output = {
        "lastUpdated": datetime.utcnow().strftime("%Y-%m-%d"),
        "items": new_items
    }

    with open("content.json", "w") as f:
        json.dump(output, f, indent=2)
        
    print(f"Updated content.json with {len(new_items)} items.")
