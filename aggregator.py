import feedparser
import json
from datetime import datetime

# Feeds tailored for EditorInspo
SOURCES = [
    # YouTube feeds use the channel ID
    {"name": "Video Copilot", "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCw9S4RDEE7n71jY_RkY70Lw", "type": "tutorial"},
    {"name": "School of Motion", "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCz22I74rW2cwe-0bQ-O20YQ", "type": "tutorial"},
    {"name": "Lesterbanks", "url": "https://lesterbanks.com/feed/", "type": "inspiration"}
]

def fetch_content():
    items = []
    for source in SOURCES:
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries[:3]: # Grab top 3 latest posts from each
                
                # Extract thumbnail automatically
                thumbnail = ""
                if "media_thumbnail" in entry:
                    thumbnail = entry.media_thumbnail[0]["url"]
                    
                # Extract tags automatically, fallback to defaults
                tags = []
                if "tags" in entry:
                    tags = [tag.term.lower() for tag in entry.tags][:2]
                if not tags:
                    tags = ["after effects", "editing"]

                item = {
                    "id": entry.get("id", entry.get("link", "")),
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "type": source["type"],
                    "tags": tags,
                    "thumbnail": thumbnail,
                    "source": source["name"]
                }
                items.append(item)
        except Exception as e:
            print(f"Error fetching {source['name']}: {e}")
            
    return items

if __name__ == "__main__":
    new_items = fetch_content()
    
    # Structure matches your Android ContentResponse
    output = {
        "lastUpdated": datetime.utcnow().strftime("%Y-%m-%d"),
        "items": new_items
    }

    with open("content.json", "w") as f:
        json.dump(output, f, indent=2)
        
    print(f"Successfully wrote {len(new_items)} items to content.json.")
