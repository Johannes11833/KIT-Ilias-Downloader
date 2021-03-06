#!/usr/bin/python3
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from threading import Event
from typing import Dict

import argh
from argh import arg
from dotenv import load_dotenv

from files import load_json_dict, save_json_dict, get_local_file_list
from scheduler import TimeScheduler, Task
from setup_cli import setup_ilias_downloader, setup_rclone

F_NAME_REPORT = 'data/ilias_upload_report.json'
EXECUTABLES_FOLDER_PATH = Path('data/kit-downloader')
config = {}


def load_config() -> Dict:
    cfg = {}

    # load environment variables (in development)
    load_dotenv()

    # create key and default value pairs
    key_defaults = [
        ['ILIAS_DOWNLOADER_USER_NAME', None],
        ['ILIAS_DOWNLOADER_PASSWORD', None],
        ['ILIAS_DOWNLOADER_CLOUD_OUTPUT_PATH', 'output'],
        ['ILIAS_DOWNLOADER_SYNC_URL', None],
        ['ILIAS_DOWNLOADER_JOBS', 10],
        ['ILIAS_DOWNLOADER_RATE', 100],
        ['ILIAS_DOWNLOADER_RCLONE_REMOTE_NAME', 'IliasDL-Cloud-Drive'],
        ['ILIAS_DOWNLOADER_CLIENT_ID', None],
        ['ILIAS_DOWNLOADER_CLIENT_SECRET', None],
        ['ILIAS_DOWNLOADER_UPLOAD_TIMES', '00:00'],
    ]

    # load the environment variables
    for key, default in key_defaults:
        cfg[key] = os.getenv(key) or default

    return cfg


def download_ilias_data():
    logging.info("Starting ilias download...")

    # create the ilias downloader command
    command = str(Path(EXECUTABLES_FOLDER_PATH, 'KIT-ILIAS-downloader'))

    command += f" -U {config['ILIAS_DOWNLOADER_USER_NAME']}" \
               f" -P \"{config['ILIAS_DOWNLOADER_PASSWORD']}\"" \
               f" -o \"output\"" \
               f" --jobs  {config['ILIAS_DOWNLOADER_JOBS']}" \
               f" --rate {config['ILIAS_DOWNLOADER_RATE']}"

    if config['ILIAS_DOWNLOADER_SYNC_URL']:
        command += f" --sync-url \"{config['ILIAS_DOWNLOADER_SYNC_URL']}\""

    # execute the command
    output = subprocess.run(command, shell=True)

    if output.returncode == 0:
        # update report
        new_files_count = update_report_dict()
        logging.info(f'Downloaded {new_files_count} new file(s) from ilias. Starting upload to the cloud...')

        # upload the new file
        upload_rclone("output", config['ILIAS_DOWNLOADER_CLOUD_OUTPUT_PATH'])
    else:
        logging.error(f'Download from Ilias failed.')


def upload_rclone(output_path_local='output', output_path_remote='output'):
    r_name = config['ILIAS_DOWNLOADER_RCLONE_REMOTE_NAME']

    command = f"rclone copy --progress --ignore-existing " \
              f"\"{output_path_local}\" \"{r_name}:{output_path_remote}\""

    # execute the upload command
    output = subprocess.run(command, shell=True, stderr=subprocess.PIPE)

    # upload the updated report
    command = f"rclone copy {F_NAME_REPORT} \"{r_name}:{output_path_remote}\""
    subprocess.run(command, shell=True)

    if output.returncode == 0:
        logging.info('Cloud upload completed.')
    else:
        logging.error(f'Cloud upload failed with error message: {output.stderr}', )


def update_report_dict() -> int:
    sync_dict = load_json_dict(F_NAME_REPORT, {'upload_events': [], 'synced_files': []})
    local_files = get_local_file_list(Path('./output'))
    uploaded_files = sync_dict.get('synced_files')
    upload_events = sync_dict.get('upload_events')
    new_files = list(set(local_files).difference(uploaded_files))

    # update synced files
    sync_dict['synced_files'].extend([path.__str__() for path in new_files])

    # add new event
    upload_events.insert(0, {'time': datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), 'new_files_count': len(new_files),
                             'new_files': new_files})

    # save the update report
    save_json_dict(F_NAME_REPORT, sync_dict)

    return len(new_files)


@arg('--force_update', '-f', help='force the update immediately')
def main(force_update: bool = False):
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
    global config
    config = load_config()

    # check if username and passwords are available
    if not config['ILIAS_DOWNLOADER_USER_NAME']:
        logging.error('The Ilias username has not been set')
    elif not config['ILIAS_DOWNLOADER_PASSWORD']:
        logging.error('The Ilias password has not been set')
    else:

        # set up the ilias downloader
        setup_ilias_downloader(logging, exec_path=EXECUTABLES_FOLDER_PATH)

        # set up a cloud provider
        set_up_complete = False
        while not set_up_complete:
            set_up_complete = setup_rclone(config, logging)

        if not os.path.exists('output') or force_update:
            # this is the initial run, directly start the download and upload to the cloud
            download_ilias_data()

        # schedule automatic downloads and uploads
        upload_times = config['ILIAS_DOWNLOADER_UPLOAD_TIMES'].split()
        logging.info(f'Scheduling automatic downloads for {upload_times}')
        ts = TimeScheduler()
        for t in upload_times:
            ts.add(Task(t, download_ilias_data))
        ts.start()

        # wait until manually stopped
        Event().wait()


if __name__ == '__main__':
    argh.dispatch_command(main)
