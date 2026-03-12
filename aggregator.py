import os
import json
import hashlib
import yt_dlp
import firebase_admin
from firebase_admin import credentials, firestore

cert_dict = json.loads(os.environ.get('FIREBASE_CREDENTIALS'))
cred = credentials.Certificate(cert_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()

SOURCES = [
    {"name": "Video Copilot", "url": "https://www.youtube.com/channel/UCw9S4RDEE7n71jY_RkY70Lw", "type": "tutorials"},
    {"name": "School of Motion", "url": "https://www.youtube.com/channel/UCz22I74rW2cwe-0bQ-O20YQ", "type": "tutorials"},
    {"name": "Film Riot", "url": "https://www.youtube.com/channel/UC6P24bhhCmMqcC07VeqJZqw", "type": "tutorials"}
]

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
    ydl_opts = {
        'extract_flat': True,
        'playlistend': 5,
        'quiet': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for source in SOURCES:
            try:
                print(f"Fetching from {source['name']}...")
                info = ydl.extract_info(source["url"], download=False)
                
                if 'entries' not in info or not info['entries']:
                    print(f"  -> WARNING: 0 videos found for {source['name']}.")
                    continue
                
                for entry in info['entries']:
                    title = entry.get("title", "Untitled")
                    video_id = entry.get("id", "")
                    
                    if not video_id: continue
                    
                    url = f"https://www.youtube.com/watch?v={video_id}"
                    thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                    
                    text_to_scan = title.lower()
                    tags = set([source["type"]]) 
                    for keyword, tag in TAG_KEYWORDS.items():
                        if keyword in text_to_scan:
                            tags.add(tag)
                    
                    item = {
                        "title": title,
                        "url": url,
                        "type": source["type"],
                        "tags": list(tags)[:4], 
                        "thumbnail": thumbnail,
                        "source": source["name"],
                        "timestamp": firestore.SERVER_TIMESTAMP
                    }
                    
                    doc_id = hashlib.md5(url.encode()).hexdigest()
                    db.collection('content').document(doc_id).set(item, merge=True)
                    count += 1
                    
            except Exception as e:
                print(f"CRITICAL ERROR parsing {source['name']}: {e}")
                
    return count

if __name__ == "__main__":
    print(f"Successfully uploaded {fetch_and_upload()} items to Firebase!")
