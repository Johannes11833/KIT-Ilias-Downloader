import logging
import os
import subprocess
from threading import Event
from typing import Dict

from dotenv import load_dotenv

from cloud.cloud_uploader import CloudUploader
from scheduler import TimeScheduler, Task


def load_config() -> Dict:
    cfg = {}

    # load environment variables (in development)
    load_dotenv()

    # create key and default value pairs
    key_defaults = [
        ['ILIAS_DOWNLOADER_USER_NAME', None],
        ['ILIAS_DOWNLOADER_PASSWORD', None],
        ['ILIAS_DOWNLOADER_OUTPUT_PATH', './output'],
        ['ILIAS_DOWNLOADER_SYNC_URL', None],
        ['ILIAS_DOWNLOADER_JOBS', 10],
        ['ILIAS_DOWNLOADER_RATE', 100],
        ['ILIAS_DOWNLOADER_USE_KEY_RING', False],
    ]

    # load the environment variables
    for key, default in key_defaults:
        cfg[key] = os.getenv(key) or default

    return cfg


def download_ilias_data():
    # create the ilias downloader command
    command = f"~/.cargo/bin/KIT-ILIAS-downloader" \
              f" -U {config['ILIAS_DOWNLOADER_USER_NAME']}" \
              f" -P \"{config['ILIAS_DOWNLOADER_PASSWORD']}\"" \
              f" -o \"{config['ILIAS_DOWNLOADER_OUTPUT_PATH']}\"" \
              f" --jobs  {config['ILIAS_DOWNLOADER_JOBS']}" \
              f" --rate {config['ILIAS_DOWNLOADER_RATE']}"

    if config['ILIAS_DOWNLOADER_SYNC_URL']:
        command += f" --sync-url \"{config['ILIAS_DOWNLOADER_SYNC_URL']}\""

    # execute the command
    subprocess.run(command, shell=True)

    # upload the files to the cloud
    db.upload_new_files('./ilias')


if __name__ == '__main__':
    # create data folder
    if not os.path.exists('./data'):
        os.makedirs('./data')

    # setup logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler('./data/log.log'),
            logging.StreamHandler()
        ]
    )

    # load the config
    config = load_config()

    # set up the cloud uploader
    db = CloudUploader(logger=logging)

    # check if username and passwords are available
    if not config['ILIAS_DOWNLOADER_USER_NAME']:
        logging.error('The Ilias username has not been set')
    elif not config['ILIAS_DOWNLOADER_PASSWORD']:
        logging.error('The Ilias password has not been set')
    else:
        # # schedule automatic downloads
        # ts = TimeScheduler()
        # ts.add(Task('17:32:20', download_ilias_data))
        # ts.start()

        db.upload_new_files('./ilias')

        # wait until manually stopped
        Event().wait()
