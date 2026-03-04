import os
import re
from googleapiclient.discovery import build

# --- ANTICLANCARIA: BOT OF ALLIANCE (BOA) ---
API_KEY = os.environ.get("YT_API_KEY")
VIDEO_ID = os.environ.get("VIDEO_ID")
# NEW: The Scout provides a summary of the video to prevent false positives
VIDEO_SUMMARY = os.environ.get("VIDEO_SUMMARY", "").lower() 

DISCLAIMER = (
    "> [!IMPORTANT]\n"
    "> **Thanks for using REPORT-THE-MACHINES.** Please remember this is not 100% accurate yet, "
    "and always double check users before reporting.\n\n"
    "---"
)

def is_rational_human(text, bio, vids, subs):
    """
    UDAAC Rationality Check: Filters out 'Safe' patterns to prevent friendly fire.
    """
    text_lower = text.lower()
    
    # 1. The 'Human' Emoji check (The 🫩🥀✌️💔 filter)
    human_emojis = ["🫩", "🥀", "✌️", "💔"]
    has_human_vibes = any(e in text for e in human_emojis)
    
    # 2. Context Awareness: Check if the comment matches the video topic
    # If the user mentioned keywords from the summary, they are likely human
    context_keywords = [word for word in VIDEO_SUMMARY.split() if len(word) > 3]
    matches_context = any(word in text_lower for word in context_keywords) if context_keywords else False

    # 3. Final Verification Logic
    # If they use human emojis, have no scam links, and don't fit the 'High Sub/No Vid' bot profile:
    has_link = len(re.findall(r'(https?://[^\s]+|www\.[^\s]+)', bio)) > 0
    is_suspicious_profile = (vids == 0 and subs > 1000)

    if (has_human_vibes or matches_context) and not has_link and not is_suspicious_profile:
        return True # It's a Human.
    
    return False

def is_bot_text(text):
    text_lower = text.lower()
    # Updated patterns for Grade B Persona Bots
    patterns = ["loving and caring", "helped me understand", "aesthetic", "✨", "1.", "2.", "3."]
    return any(p in text_lower for p in patterns)

def check_channels_batch(youtube, channel_ids, comment_map):
    request = youtube.channels().list(
        part="statistics,snippet",
        id=",".join(channel_ids)
    )
    res = request.execute()
    
    for item in res.get("items", []):
        c_id = item["id"]
        snippet = item["snippet"]
        stats = item["statistics"]
        bio = snippet.get("description", "").lower()
        
        vids = int(stats.get("videoCount", 0))
        subs = int(stats.get("subscriberCount", 0))
        comment_text = comment_map.get(c_id, "")
        
        # --- THE RATIONALITY FILTER ---
        if is_rational_human(comment_text, bio, vids, subs):
            continue # Skip this user, they passed the human check.

        # --- THE THREAT DETECTION ---
        has_link = len(re.findall(r'(https?://[^\s]+|www\.[^\s]+)', bio)) > 0
        is_hardcore = (vids == 0 and has_link)
        is_phrase = is_bot_text(comment_text)

        if is_hardcore or is_phrase:
            print(f"### [!] NEUTRALIZED: {snippet['title']}")
            print(f"- **Target Grade:** {'Grade A (Scammer)' if is_hardcore else 'Grade B (Persona)'}")
            print(f"- **Logic:** {'Pattern Match' if is_phrase else 'Metadata Signature'}")
            print(f"- **Comment:** \"{comment_text}\"")
            print(f"- **Intel:** https://youtube.com/channel/{c_id}\n")
