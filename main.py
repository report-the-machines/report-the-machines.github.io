import string
from googleapiclient.discovery import build
import re

# --- CONFIGURATION ---
API_KEY = "PASTE_API_KEY"

youtube = build("youtube", "v3", developerKey=API_KEY)

def is_bot_text(text):
    text_lower = text.lower()
    # Patterns for Sleeper Bots & Aesthetic Script clusters
    patterns = ["loving and caring", "helped me understand", "aesthetic", "✨", "1.", "2.", "3."]
    return any(p in text_lower for p in patterns)

def check_channels_batch(channel_ids, comment_map):
    request = youtube.channels().list(
        part="statistics,snippet",
        id=",".join(channel_ids)
    )
    res = request.execute()
    
    for item in res.get("items", []):
        c_id = item["id"]
        snippet = item["snippet"]
        channel_stats = item["statistics"]
        bio = snippet.get("description", "").lower()
        
        # Metadata filtering
        subs = int(channel_stats.get("subscriberCount", 0))
        vids = int(channel_stats.get("videoCount", 0))
        comment_text = comment_map.get(c_id, "")
        
        # The "Clanker" Trap: Link in Bio + High Subs + No Videos
        has_link = len(re.findall(r'(https?://[^\s]+|www\.[^\s]+)', bio)) > 0
        is_hardcore = (vids == 0 and has_link)
        is_phrase = is_bot_text(comment_text)

        if is_hardcore or is_phrase:
            print(f"\n[!] NEUTRALIZED: {snippet['title']}")
            print(f"    > Logic: {'Pattern Match' if is_phrase else 'Metadata Signature'}")
            print(f"    > Comment: \"{comment_text}\"")
            print(f"    > Intelligence: https://youtube.com/channel/{c_id}")

def hunt(video_id):
    print(f"\n[*] DEPLOYING TO TARGET: {video_id}")
    try:
        # Fetching top-level threads
        request = youtube.commentThreads().list(
            part="snippet", videoId=video_id, maxResults=100, textFormat="plainText"
        )
        
        while request:
            response = request.execute()
            ids, mapping = [], {}
            
            for item in response.get("items", []):
                s = item["snippet"]["topLevelComment"]["snippet"]
                c_id = s["authorChannelId"]["value"]
                ids.append(c_id)
                mapping[c_id] = s["textDisplay"]
            
            # Process in batches of 50 (Max API limit per call)
            for i in range(0, len(ids), 50):
                check_channels_batch(ids[i:i+50], mapping)
            
            request = youtube.commentThreads().list_next(request, response)
            
    except Exception as e:
        print(f"\n[!] ERROR IN DEPLOYMENT: {e}")

if __name__ == "__main__":
    print("========================================")
    print("      ANTICLANCARIA: BOT OF ALLIANCE    ")
    print("      REPORT THE MACHINES.             ")
    print("      Numquam sciabis qui ego sum.     ")
    print("========================================\n")
    
    while True:
        target = input("Input Video URL or ID (or 'exit'): ").strip()
        if target.lower() == 'exit':
            print("\nShutting down. Machinis cessant.")
            break
        
        # Regex to pull ID from any YouTube link format
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", target)
        v_id = match.group(1) if match else target
        
        if len(v_id) == 11:
            hunt(v_id)
            print("\n[*] Target audit complete. Standing by.")
        else:
            print("[!] Invalid Target ID.")
