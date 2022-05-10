import logging
import os
import subprocess
from threading import Event
from typing import Dict

from dotenv import load_dotenv

from console_input import show_selection_dialog
from scheduler import TimeScheduler, Task


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
    command = f"KIT-ILIAS-downloader" \
              f" -U {config['ILIAS_DOWNLOADER_USER_NAME']}" \
              f" -P \"{config['ILIAS_DOWNLOADER_PASSWORD']}\"" \
              f" -o \"output\"" \
              f" --jobs  {config['ILIAS_DOWNLOADER_JOBS']}" \
              f" --rate {config['ILIAS_DOWNLOADER_RATE']}"

    if config['ILIAS_DOWNLOADER_SYNC_URL']:
        command += f" --sync-url \"{config['ILIAS_DOWNLOADER_SYNC_URL']}\""

    # execute the command
    subprocess.run(command, shell=True)

    logging.info('Download from ilias completed. Starting upload to the cloud...')

    # upload the new file
    upload_rclone("output", config['ILIAS_DOWNLOADER_CLOUD_OUTPUT_PATH'])


def setup_rclone():
    # check if rclone is installed
    from shutil import which
    if which('rclone') is None:
        raise Exception('Rclone is not installed on this system. It is need to backup the files to the cloud!'
                        'Install it here: https://rclone.org/')

    r_name = config['ILIAS_DOWNLOADER_RCLONE_REMOTE_NAME']

    # get the available remotes
    remotes = subprocess.check_output('rclone listremotes', shell=True, encoding='UTF-8').split()

    if f"{r_name}:" not in remotes:
        # setup is not yet complete
        options = ["Yes (start interactive setup)", "No (terminate)"]
        i = show_selection_dialog(options, ['y', 'n'],
                                  f'The remote \'{r_name}\' has not been set up yet. Set it up now?')

        if i == 'y':
            options_display = ['GoogleDrive', 'Dropbox', 'OneDrive', "Other (manual setup using rclone)"]
            options = ["drive", 'dropbox', 'onedrive', None]

            index = show_selection_dialog(options_display, title='Choose your cloud provider')
            if index < len(options) - 1:
                # set up the selected cloud
                command = f"rclone config create \"{r_name}\" {options[index]}"

                if config['ILIAS_DOWNLOADER_CLIENT_ID'] and config['ILIAS_DOWNLOADER_CLIENT_SECRET']:
                    logging.info('Using the provided client id and client secret.')

                    command += f" --{options[index]}-client-id \"{config['ILIAS_DOWNLOADER_CLIENT_ID']}\"" \
                               f" --{options[index]}-client-secret \"{config['ILIAS_DOWNLOADER_CLIENT_SECRET']}\""
                else:
                    logging.warning('The drive client id and the client secret have not been set. Using defaults.')
            else:
                command = "rclone config"

            # run the setup command
            subprocess.run(command, shell=True)
        else:
            quit()
    else:
        # setup is complete
        return True


def upload_rclone(output_path_local='output', output_path_remote='output'):
    r_name = config['ILIAS_DOWNLOADER_RCLONE_REMOTE_NAME']

    command = f"rclone copy --progress --ignore-existing " \
              f"\"{output_path_local}\" \"{r_name}:{output_path_remote}\""

    # execute the upload command
    subprocess.run(command, shell=True)

    logging.info('Cloud upload completed.')


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

    # check if username and passwords are available
    if not config['ILIAS_DOWNLOADER_USER_NAME']:
        logging.error('The Ilias username has not been set')
    elif not config['ILIAS_DOWNLOADER_PASSWORD']:
        logging.error('The Ilias password has not been set')
    else:
        set_up_complete = False

        # set up a cloud provider
        while not set_up_complete:
            set_up_complete = setup_rclone()

        if not os.path.exists('output'):
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
