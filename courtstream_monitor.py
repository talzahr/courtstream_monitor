import yt_dlp
import time
import datetime
import logging

# Begin Config
LIVESTREAM_URL = "https://video.ibm.com/channel/23891775"
CHECK_INTERVAL_SECONDS = 20 * 60
START_HOUR = 8  # 08:00
END_HOUR = 13  # 13:00
START_MINUTE = 0
END_MINUTE = 0
# Weekdays: 0=Monday, 1=Tuesday, ..., 6=Sunday
DAYS_TO_RUN = [0, 1, 2, 3, 4]  # Monday to Friday

LOG_FILE = "streams.log"
# End Config

# Logging Init
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()  # Also print to console
    ]
)

def is_within_schedule():
    now = datetime.datetime.now()
    current_time = now.time()
    start_time = datetime.time(START_HOUR, START_MINUTE)
    end_time = datetime.time(END_HOUR, END_MINUTE)

    if now.weekday() not in DAYS_TO_RUN:
        return False
    if not (start_time <= current_time < end_time): # Check runs *until* end_time
        return False
    return True

def check_livestream(url):
    ydl_opts = {
        'quiet': True,        # Suppress yt-dlp's own console output
        'no_warnings': True,  # Suppress warnings
        'simulate': True,     # Don't download
        'extract_flat': 'in_playlist', # For channels, don't try to list all videos in detail
                                       # Speeds up the check significantly for channel URLs
        'forcejson': True,
        # 'skip_download': True,
    }

    logging.info(f"Attempting to check URL: {url}")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)

            if info_dict:
                title = info_dict.get('title', 'N/A')
                uploader = info_dict.get('uploader', 'N/A')
                logging.info(f"SUCCESS: yt-dlp processed URL. Title: '{title}', Uploader: '{uploader}'")
                return True
            else:
                logging.warning(f"WARNING: yt-dlp returned no info_dict for {url}, but no error raised.")
                return False

    except yt_dlp.utils.DownloadError as e:
        logging.error(f"STREAM NOT ONLINE")
        return False
    except Exception as e:
        logging.error(f"UNEXPECTED ERROR while checking {url}: {e}")
        return False

def main():
    logging.info("Livestream checker script started.")
    logging.info(f"Checking URL: {LIVESTREAM_URL}")
    logging.info(f"Interval: {CHECK_INTERVAL_SECONDS / 60} minutes")
    logging.info(f"Schedule: Days {DAYS_TO_RUN} (Mon-Fri) between {START_HOUR:02d}:{START_MINUTE:02d} and {END_HOUR:02d}:{END_MINUTE:02d}")

    try:
        while True:
            if is_within_schedule():
                logging.info("Within scheduled time. Proceeding with check.")
                status_ok = check_livestream(LIVESTREAM_URL)
                if status_ok:
                    pass
                else:
                    pass
                
                time.sleep(CHECK_INTERVAL_SECONDS)
            else:
                logging.debug("Outside scheduled time. Sleeping for 5 minutes before re-checking schedule.")
                time.sleep(5 * 60) # Sleep for 5 minutes

    except KeyboardInterrupt:
        logging.info("Script interrupted by user. Exiting.")
    except Exception as e:
        logging.critical(f"CRITICAL SCRIPT ERROR: {e}", exc_info=True)
    finally:
        logging.info("Livestream checker script stopped.")

if __name__ == "__main__":
    try:
        import yt_dlp
    except ImportError:
        print("Error: The 'yt-dlp' library is not installed.")
        print("Please install it by running: pip install yt-dlp")
        exit(1)
        
    main()