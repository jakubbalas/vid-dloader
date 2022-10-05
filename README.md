GSheets Video downloader

This small script gets video links from google spreadsheets and downloads it 
to the desired folder.

How to run this script:
1) If you don't have already, create GCP IAM service user
2) Generate and copy service user token.json to this folder
3) Create a new spreadsheet and have sheet1 reserved for links to download
4) Fill the first column with link
5) Second column is optional and works as a subfolder / subcategory.
6) Third column is reserved for the script
7) Copy .env.example to .evn and fill it in.
8) Use direnv or something similar to load env variables
9) Run and profit

Note:
While running, some ISPs can block the access and cause connection timeout so try to run it with VPN active.
