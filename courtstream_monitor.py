__version__ = "0.1"
__revision__ = 3

import yt_dlp
import yt_dlp.utils # Need this to suppress the outputs. I tried 'quite' and 'no_warnings' opts but no dice.
import time
import datetime
import logging

# Config
LIVESTREAM_URL = "https://video.ibm.com/channel/23891775"
CHECK_INTERVAL_SECONDS = 20 * 60
START_HOUR = 8
END_HOUR = 13
START_MINUTE = 0
END_MINUTE = 0
DAYS_TO_RUN = [0, 1, 2, 3, 4]

LOG_FILE = "streams.log"

# Logging init
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Easy call to supress outputs from the console, similar to _YDLLogger class in yt_dlp's utils.py
class YtdlpSilentLogger:
    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass

def is_within_schedule():
    now = datetime.datetime.now()
    current_time = now.time()
    start_time = datetime.time(START_HOUR, START_MINUTE)
    end_time = datetime.time(END_HOUR, END_MINUTE)

    if now.weekday() not in DAYS_TO_RUN:
        return False
    if not (start_time <= current_time < end_time):
        return False
    return True

def check_livestream(url):
    ydl_opts = {
        'quiet': True,                 # some limnitations may apply, lol
        'no_warnings': True,
        'simulate': True,              # Don't want to download, just know it's online
        'extract_flat': 'in_playlist',
        'forcejson': True,
        'logger': YtdlpSilentLogger(), # The logging class above
    }

    logging.info(f"Attempting to check URL: {url}")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)

            if info_dict:
                title = info_dict.get('title', 'N/A')
                uploader = info_dict.get('uploader', 'N/A')
                is_live = info_dict.get('is_live')

                if is_live is True:
                    logging.info(f"(!!!) LIVESTREAM ONLINE: URL: {url}, Title: '{title}', Uploader: '{uploader}'")
                    return True
                elif is_live is False:
                    logging.info(f"STREAM EXISTS BUT NOT LIVE: URL: {url}, Title: '{title}', Uploader: '{uploader}'")
                    return False
                else:
                    logging.info(f"METADATA RETRIEVED (is_live: {is_live}): URL: {url}. Title: '{title}', Uploader: '{uploader}'")
                    return False
            else:
                logging.warning(f"WARNING: yt-dlp returned no info_dict for {url}, but no error raised.")
                return False

    except yt_dlp.utils.DownloadError as e:
        logging.info(f"STREAM NOT ONLINE")
        return False
    except Exception as e:
        logging.error(f"UNEXPECTED ERROR while checking {url}: {e}", exc_info=True)
        return False

def main():
    logging.info("Livestream checker script started.")
    logging.info(f"Checking URL: {LIVESTREAM_URL}")
    logging.info(f"Interval: {CHECK_INTERVAL_SECONDS / 60} minutes")
    logging.info(f"Schedule: Days {DAYS_TO_RUN} (Mon-Fri) between {START_HOUR:02d}:{START_MINUTE:02d} and {END_HOUR:02d}:{END_MINUTE:02d}")

    try: # Suppress traceback spam when CTRL-C'd/SIGINT
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
                time.sleep(5 * 60)

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