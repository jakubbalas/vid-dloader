import os
import sys
import loguru
import yt_dlp as youtube_dl
import sqlite3
from path import Path
from enum import IntEnum


class LinkState(IntEnum):
    TO_PROCESS = 1
    TO_DOWNLINK = 2
    IGNORE = 3
    DONE = 4
    ERROR = 5


MAX_RETRIES = 5
logger = loguru.logger
SOURCE_DB = Path(os.environ.get("SOURCE_DB"))
DESTINATION = Path(os.environ.get("DESTINATION"))

if not (SOURCE_DB and DESTINATION):
    raise Exception("Improperly configured, check .env.examples")


def dload_with_retries(
    dloader: youtube_dl.YoutubeDL,
    url: str,
    retry_count: int,
    remove_errors: bool
):
    try:
        dloader.download([url])
        update_link_state(url, LinkState.DONE)
       
    except Exception as e:
        if retry_count < MAX_RETRIES:
            retry_count += 1
            logger.warning(
                f"Error occured, making retry #{retry_count}; Error: {str(e)}"
            )
            dload_with_retries(dloader, url, retry_count, remove_errors)
        else:
            if remove_errors:
                update_link_state(url, LinkState.DONE)
            logger.error(f"Ran out of retries for {url} ; Error: {str(e)}")


def dload(remove_errors: bool):
    if not (SOURCE_DB.exists() and DESTINATION.exists()):
        raise Exception("Source and destination must exist")
    

    sql = f"SELECT url FROM speclinks where process = {LinkState.TO_DOWNLINK}"
    con = sqlite3.connect(SOURCE_DB)
    cur = con.cursor()
    cur.execute(sql)
    res = cur.fetchall()
    con.close()

    for url in res:

        ydl_opts = {
            "outtmpl": DESTINATION / "%(title)s.%(ext)s",
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            dload_with_retries(ydl, url[0], 0, remove_errors)


def update_link_state(url, state):
        sql = "UPDATE speclinks SET process = ? WHERE url = ?"
        con = sqlite3.connect(SOURCE_DB)
        cur = con.cursor()
        cur.execute(sql, [state, url])
        con.commit()
        con.close()


if __name__ == "__main__":
    logger.info("Welcome to vid downloader. Now sit back and enjoy :)")
    logger.info("If you need to remove errors, run the app with --remove-errors argument")
    remove_errors = "--remove-errors" in sys.argv
    dload(remove_errors)
