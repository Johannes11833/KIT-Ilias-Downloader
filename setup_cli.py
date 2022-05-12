from pathlib import Path
import subprocess

from console_input import show_selection_dialog


def unix_like() -> bool:
    import sys
    if 'win' in sys.platform:
        return False
    else:
        return True


def setup_ilias_downloader(config, logging):
    from shutil import which
    if unix_like() and which(f'{Path.home()}/.cargo/bin/KIT-ILIAS-downloader') is None:
        options = ['yes', 'no']
        i = show_selection_dialog(options, ['y', 'n'],
                                  f'The KIT-ILIAS-downloader is not installed on this system. Auto install it?')

        if i == 'y':
            if which('cargo') is None:
                # install rust first

                logging.info('Rust is not installed. Trying to auto install it...')
                output = subprocess.run("curl https://sh.rustup.rs -sSf | sh -s -- -y", shell=True)

                if output.returncode == 0:
                    logging.info('Rust was successfully installed.')
                else:
                    raise Exception('Failed to auto install rust. '
                                    'Please try installing it manually at: https://www.rust-lang.org/tools/install')

            # install the ilias downlaoder cli tool
            output = subprocess.run("cargo install --all-features "
                                    "--git 'https://github.com/FliegendeWurst/KIT-ILIAS-downloader' --branch stable",
                                    shell=True)

            if output.returncode == 0:
                logging.info('The KIT-ILIAS-downloader CLI tool was successfully installed.')
            else:
                raise Exception('Failed to install the KIT-ILIAS-downloader CLI tool.'
                                'Please try manually installing it at: '
                                'https://github.com/fliegendewurst/kit-ilias-downloader')

        else:
            quit()


def setup_rclone(config, logging):
    # check if rclone is installed
    from shutil import which
    if which('rclone') is None:
        raise Exception('Rclone is not installed on this system. It is needed to backup the files to the cloud!'
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
