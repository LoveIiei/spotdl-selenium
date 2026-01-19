import os
import time
import yt_dlp
from tqdm import tqdm
from playwright.sync_api import sync_playwright

# --- 1. Logger & Config (Same as before) ---
class FileLogger:
    def __init__(self):
        with open("download_log.txt", "w") as f:
            f.write("--- Download Session Log ---\n")

    def debug(self, msg): pass

    def warning(self, msg):
        with open("download_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[WARNING] {msg}\n")

    def error(self, msg):
        with open("download_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[ERROR] {msg}\n")

# --- 2. The New Playwright Scraper ---
def scrape_spotify(url):
    song_list = []
    print("🕵️  Launching Playwright (Headless)...")
    
    with sync_playwright() as p:
        # Launch browser (headless=True is faster)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"🌍 Going to {url}...")
        page.goto(url)
        
        # Playwright auto-waits for the tracklist to exist.
        # We look for the tracklist row.
        try:
            page.locator("div[data-testid='tracklist-row']").first.wait_for(timeout=10000)
        except:
            print("⚠️ Could not load tracklist. Is the link valid?")
            browser.close()
            return []

        # --- Infinite Scroll Logic ---
        print("📜 Scrolling to load all songs...")
        last_height = page.evaluate("document.body.scrollHeight")
        
        while True:
            # Scroll to bottom
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            # Wait a bit for Spotify to fetch new rows (Playwright's version of sleep)
            page.wait_for_timeout(1500) 
            
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
        # --- Extraction ---
        # Locate all rows
        rows = page.locator("div[data-testid='tracklist-row']")
        count = rows.count()
        print(f"✅ Found {count} tracks.")

        # Iterate through handles
        for i in range(count):
            try:
                # Scoping: Get the i-th row
                row = rows.nth(i)
                
                # Inside that row, find the title div
                # We use specific attributes to be precise
                title_locator = row.locator("div[dir='auto']").first
                
                title = title_locator.text_content()
                if title and title not in song_list:
                    song_list.append(title)
            except Exception as e:
                continue
        
        browser.close()
        
    return song_list

# --- 3. The Downloader (Same as before) ---
def download_tracks(song_list, download_folder):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{download_folder}/%(title)s.%(ext)s',
        'writethumbnail': True,
        'logger': FileLogger(),
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata', 'add_metadata': True}
        ],
    }

    print(f"📂 Saving to: {download_folder}")
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        pbar = tqdm(song_list, unit="song", ncols=100)
        for song in pbar:
            pbar.set_description(f"Processing: {song[:20]:<20}")
            try:
                ydl.download([f"ytsearch1:{song} Audio"])
            except Exception:
                pbar.write(f"❌ Failed: {song}")

# --- 4. Main Execution ---
if __name__ == "__main__":
    link = input("🔗 Spotify Playlist Link: ")
    folder = os.path.join(os.getcwd(), "downloads")
    
    songs = scrape_spotify(link)
    
    if songs:
        download_tracks(songs, folder)
        print("\n✨ All operations finished!")
    else:
        print("⚠️ No songs found.")