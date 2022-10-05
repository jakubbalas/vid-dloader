import os
import gspread
import loguru
import youtube_dl
from path import Path
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
SUCCESS_SIGNATURE = "1"
MAX_RETRIES = 3
COLUMNS = {
    "video_link": 0,
    "placement": 1,
    "result": 2,
}

logger = loguru.logger


def dload_with_retries(
    dloader: youtube_dl.YoutubeDL,
    sheet: gspread.worksheet.Worksheet,
    link: str,
    row_number,
    retry_count: int,
):
    try:
        dloader.download([link])
        # cells start from 1, that's why we add 1
        sheet.update_cell(row_number, COLUMNS["result"] + 1, SUCCESS_SIGNATURE)
    except Exception as e:
        sheet.update_cell(row_number, COLUMNS["result"] + 1, str(e))
        if retry_count < MAX_RETRIES:
            retry_count += 1
            logger.warning(
                f"Error occured, making retry #{retry_count}; Error: {str(e)}"
            )
            dload_with_retries(dloader, sheet, link, row_number, retry_count)
        else:
            logger.error(f"Ran out of retries for {link} ; Error: {str(e)}")


def get_save_path(row):
    root_folder = Path(os.environ.get("DESTINATION_PATH").strip())
    if not root_folder.exists():
        raise Exception(f"Please create root folder {root_folder.abspath()}")
    path = (
        root_folder
        if len(row) < (COLUMNS["placement"] + 1)
        else root_folder / str(row[COLUMNS["placement"]])
    )
    if not path.exists():
        path.makedirs()
    return path


def check_env():
    required_envs = ["DESTINATION_PATH", "SHEET_NAME"]
    missing = [x for x in required_envs if not os.environ.get(x)]
    if missing:
        raise Exception(f"Missing required env variables: {','.join(missing)}")


def dload():
    creds = ServiceAccountCredentials.from_json_keyfile_name("token.json", SCOPE)
    check_env()
    sheet_name = os.environ.get("SHEET_NAME").strip()
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    values = sheet.get_all_values()

    for row_number, row in zip(range(1, len(values) + 1), values):
        if (
            len(row) == len(COLUMNS)
            and str(row[COLUMNS["result"]]) == SUCCESS_SIGNATURE
        ):
            continue

        ydl_opts = {
            "outtmpl": get_save_path(row) / "%(title)s.%(ext)s",
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            dload_with_retries(ydl, sheet, row[COLUMNS["video_link"]], row_number, 0)


if __name__ == "__main__":
    logger.info("Welcome to vid downloader. Now sit back and enjoy :)")
    dload()
