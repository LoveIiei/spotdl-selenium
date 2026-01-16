import os
import time
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

import yt_dlp

def setup_driver():
    """Initializes a headless Firefox driver."""
    options = webdriver.FirefoxOptions()
    #options.add_argument("--headless")  # Run without opening a window
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")  # Suppress console logs
    
    # helper to manage driver version automatically
    service = Service(GeckoDriverManager().install())
    return webdriver.Firefox(service=service, options=options)

def scrape_spotify_playlist(url):
    """Scrapes song names from a Spotify playlist URL."""
    driver = setup_driver()
    song_list = []
    
    print(f"Fetching playlist: {url}...")
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        
        # Wait for the tracklist to load
        # Note: Spotify classes (like 'Type__TypeElement...') are hashed and change often.
        # It is often safer to look for the container having role="row" or specific aria-labels.
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='tracklist-row']")))

        last_height = driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5) # Wait for lazy loading
            
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Parse the page source after full scroll
        
        # We try to find elements with the specific track name testid
        tracks = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='tracklist-row']")
        
        print(f"Found {len(tracks)} rows. Extracting names...")

        for track in tracks:
            try:
                # This selector targets the song title specifically inside the row
                title_element = track.find_element(By.CSS_SELECTOR, "div[dir='auto']")
                song_name = title_element.text
                
                # artist_element = track.find_element(By.CSS_SELECTOR, "a[href*='/artist/']") 
                
                if song_name and song_name not in song_list:
                    song_list.append(song_name)
            except Exception:
                continue

    except Exception as e:
        print(f"Error scraping Spotify: {e}")
    finally:
        driver.quit()
        
    return song_list

class FileLogger:
    def __init__(self):
        # Clear the log file on new run (optional)
        with open("download_log.txt", "w") as f:
            f.write("--- Download Session Log ---\n")

    def debug(self, msg):
        # We don't want to see debug info, just write to file
        with open("download_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[DEBUG] {msg}\n")

    def warning(self, msg):
        # This catches the specific "web_safari" warning you mentioned
        with open("download_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[WARNING] {msg}\n")

    def error(self, msg):
        # We generally want to see errors in console, but we can also log them
        print(f"\n[ERROR] {msg}") 
        with open("download_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[ERROR] {msg}\n")

def download_tracks(song_list, download_folder):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{download_folder}/%(title)s.%(ext)s',
        'writethumbnail': True,
        
        # 2. Inject our custom logger
        'logger': FileLogger(),
        
        # 3. Suppress yt-dlp's default console output so it doesn't break our progress bar
        'quiet': True, 
        'no_warnings': True, 
        
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata', 'add_metadata': True}
        ],
    }

    # 4. Wrap the loop in tqdm for the visual progress bar
    # ncols=100 makes the bar fixed width, nice and clean
    # unit="song" changes the counter to "1/10 songs" instead of "it/s"
    print(f"Logs are being saved to: {os.getcwd()}/download_log.txt")
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # We use 'pbar' so we can update the description dynamically
        pbar = tqdm(song_list, unit="song", ncols=100)
        
        for song in pbar:
            # Update the text next to the bar to show current song
            pbar.set_description(f"Processing: {song[:20]}...") 
            
            try:
                # We don't need print() anymore, the bar handles the visuals
                ydl.download([f"ytsearch1:{song} Audio"]) 
            except Exception as e:
                # Use pbar.write() to print without breaking the bar layout
                pbar.write(f"Failed: {song}")

if __name__ == "__main__":
    link = input("What's the Spotify link: ")
    folder = os.path.join(os.getcwd(), "spotifydl")
    
    songs = scrape_spotify_playlist(link)
    
    if songs: 
        print(f"Successfully scraped {len(songs)} songs.")
        download_tracks(songs, folder)
        print("All operations finished.")
    else:
        print("No songs found. Check your CSS selectors or the link.")