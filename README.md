[<img src="https://img.shields.io/docker/v/therealjohannes/kit-ilias-downloader?label=Dockerhub">](<https://hub.docker.com/repository/docker/therealjohannes/kit-ilias-downloader>)
# Auto KIT-Ilias Downloader

The "Auto KIT-Ilias Downloader" allows you to automatically upload new files from the KIT ilias page to a cloud storage.
This way you will no longer have to manually download new files from ilias.

Lots of cloud storage services are supported, including:

- Google Drive
- One Drive
- Dropbox

The whole list of supported clouds can be found here: https://rclone.org/

## Setup

To run this program, you need to install rclone:
https://rclone.org/downloads/

### Docker Setup

The easiest way to run this program is through docker. Do to so, you'll first have to manually set up a rclone remote
(cloud) outside of docker. Run

```shell
rclone config
```

and select "New remote" and follow the instructions there.
Once the setup is complete, verify that the rclone host path in docker-compose matches the one of rclone by running

```shell
rclone config file
```

(only add the path up until the rclone folder).

The docker-compose file mounts the rclone config folder to make it accessible to the rclone software inside the docker
container. Finally, start the container with the following command.

```shell
docker compose up
```

### Local Setup

The local set up is similar to the Docker one in the way, that you'll first have to set up the rclone remote of your
choice. Once that is done, start the python application by running:

```shell
python main.py
```

## Raspberry Pi Deployment

To run this app on a raspberry pi, you'll first have
to [compile the KIT-ILIAS-downloader from source](https://github.com/FliegendeWurst/KIT-ILIAS-downloader#installation).

```shell
cargo install --all-features --git 'https://github.com/FliegendeWurst/KIT-ILIAS-downloader';
```

### Docker Setup

Uncomment Option (2) in docker-compose.yml to mount the Ilias-DL executable.

### Local Setup

Inside the root of this repo, run the following command to copy the Ilias-DL executable to the project data folder:

```shell
cp ~/.cargo/bin/KIT-ILIAS-downloader data/kit-downloader;
```

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

- `WEBCAL_URL` : A URL to a web calender. Will schedule an upload 5 minutes ahead of each event

## Acknowledgements

- [KIT-ILIAS-downloader](https://github.com/FliegendeWurst/KIT-ILIAS-downloader): Does all the heavy lifting to download
  the ilias content.
- [Rclone](https://rclone.org/): Uploads the files to the cloud.

