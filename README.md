# Auto KIT-Ilias Downloader

The "Auto KIT-Ilias Downloader" allows you to automatically upload new files from the KIT ilias page to a cloud storage.
This way you will no longer have to manually download new files from ilias.

Lots of cloud storage services are supported, including:

- Google Drive
- One Drive
- Dropbox

The whole list of supported clouds can be found here: https://rclone.org/

## Installation

To run this program, you need to install rclone:
https://rclone.org/downloads/

## Environment Variables

To run this program, you will need to add the following environment variables to your .env file

- `ILIAS_DOWNLOADER_USER_NAME`

- `ILIAS_DOWNLOADER_PASSWORD`

### Optional variables

Furthermore, the following optional variables can be used to customize the behavior of the auto uploader:

- `ILIAS_DOWNLOADER_CLOUD_OUTPUT_PATH` : The path on the cloud to sync to.

- `ILIAS_DOWNLOADER_SYNC_URL` : The page on ilias that should be synced. By default, all favourites are synced.

- `ILIAS_DOWNLOADER_JOBS` : The amount of parallel jobs.

- `ILIAS_DOWNLOADER_RATE` : Requests per minute.

- `ILIAS_DOWNLOADER_RCLONE_REMOTE_NAME` : The name of the remote to use with rclone.

- `ILIAS_DOWNLOADER_CLIENT_ID` : Custom client id. Might improve the performance (together with the client secret).

- `ILIAS_DOWNLOADER_CLIENT_SECRET` : Custom client secret. Might improve the performance (together with the client id).

- `ILIAS_DOWNLOADER_UPLOAD_TIMES` : The time of the day at which we want to upload. You can also specify multiple times
  for example : `00:00 09:00` for automatic syncs at 0 and 9 o'clock.

## Acknowledgements

- [KIT-ILIAS-downloader](https://github.com/FliegendeWurst/KIT-ILIAS-downloader): Does all the heavy lifting to download
  the ilias content.
- [Rclone](https://rclone.org/): Uploads the files to the cloud.

