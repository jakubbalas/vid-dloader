import os
import gspread
import loguru
import youtube_dl
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
SUCCESS_SIGNATURE = "1"
MAX_RETRIES = 3

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
        sheet.update_cell(row_number, 2, SUCCESS_SIGNATURE)
    except Exception as e:
        sheet.update_cell(row_number, 2, str(e))
        if retry_count < MAX_RETRIES:
            retry_count += 1
            logger.warning(
                f"Error occured, making retry #{retry_count}; Error: {str(e)}"
            )
            dload_with_retries(dloader, sheet, link, row_number, retry_count)
        else:
            logger.error(f"Ran out of retries for {link} ; Error: {str(e)}")


def dload():
    creds = ServiceAccountCredentials.from_json_keyfile_name("token.json", SCOPE)
    save_path = os.environ.get("DESTINATION_PATH")
    sheet_name = os.environ.get("SHEET_NAME").strip()
    logger.info(sheet_name)
    if not save_path or not sheet_name:
        logger.error(f"save_path: {save_path}; sheet_name: {sheet_name}")
        raise Exception("Configure env variables first")
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    values = sheet.get_all_values()
    ydl_opts = {
        "outtmpl": os.path.join(save_path, "%(title)s.%(ext)s"),
    }

    for row_number, row in zip(range(1, len(values) + 1), values):
        if len(row) == 2 and str(row[1]) == SUCCESS_SIGNATURE:
            continue
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            dload_with_retries(ydl, sheet, row[0], row_number, 0)


if __name__ == "__main__":
    logger.info("Welcome to vid downloader. Now sit back and enjoy :)")
    dload()
