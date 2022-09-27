GSheets Video downloader

This small script gets video links from google spreadsheets and downloads it 
to the desired folder.

How to run this script:
1) If you don't have already, create GCP IAM service user
2) Generate and copy service user token.json to this folder
3) Create a new spreadsheet and have sheet1 reserved for links to download
4) Fill in only the first column, second column is reserved for the script
5) Copy .env.example to .evn and fill it in.
6) Use direnv or something similar to load env variables
7) Run and profit

Note:
While running, some ISPs can block the access and cause connection timeout so try to run it with VPN active.
