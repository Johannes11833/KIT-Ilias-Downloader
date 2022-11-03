import subprocess
from pathlib import Path

import requests

from console_input import show_selection_dialog


def unix_like() -> bool:
    import sys

    if "win" in sys.platform:
        return False
    else:
        return True


def setup_ilias_downloader(logging, exec_path: Path):
    if not exec_path.is_dir():
        exec_path.mkdir()
    elif (unix_like() and Path(exec_path, "KIT-ILIAS-downloader").is_file()) or (
        not unix_like() and Path(exec_path, "KIT-ILIAS-downloader.exe").is_file()
    ):
        print(f"KIT-ILIAS-downloader executable found (Unix = {unix_like()}).")
        return

    # get the newest release of the KIT-ILIAS-downloader through the GitHub api.
    r = requests.get(
        "https://api.github.com/repos/FliegendeWurst/KIT-ILIAS-downloader/releases/latest"
    )
    data = r.json()

    # download all assets of the latest release
    if r.status_code == requests.codes.ok:
        for asset in data["assets"]:
            with open(Path(exec_path, asset["name"]), "wb") as f:
                f.write(requests.get(asset["browser_download_url"]).content)

        if unix_like():
            # if on unix: make the binary file executable
            subprocess.run(
                f'chmod +x {Path(exec_path, "KIT-ILIAS-downloader")}', shell=True
            )

        logging.info(f'Successfully downloaded KIT-ILIAS-downloader {data["name"]}')
    else:
        logging.warning(
            "Could not retrieve latest  KIT-ILIAS-downloader release from GitHub!"
        )
        logging.warning(f"Code {r.status_code}: {r.content}")


def setup_rclone(config, logging):
    # check if rclone is installed
    from shutil import which

    if which("rclone") is None:
        raise Exception(
            "Rclone is not installed on this system. It is needed to backup the files to the cloud!"
            "Install it here: https://rclone.org/"
        )

    r_name = config["ILIAS_DOWNLOADER_RCLONE_REMOTE_NAME"]

    # get the available remotes
    remotes = subprocess.check_output(
        "rclone listremotes", shell=True, encoding="UTF-8"
    ).split()

    if f"{r_name}:" not in remotes:
        # setup is not yet complete
        options = ["Yes (start interactive setup)", "No (terminate)"]
        i = show_selection_dialog(
            options,
            ["y", "n"],
            f"The remote '{r_name}' has not been set up yet. Set it up now?",
        )

        if i == "y":
            options_display = [
                "GoogleDrive",
                "Dropbox",
                "OneDrive",
                "Other (manual setup using rclone)",
            ]
            options = ["drive", "dropbox", "onedrive", None]

            index = show_selection_dialog(
                options_display, title="Choose your cloud provider"
            )
            if index < len(options) - 1:
                # set up the selected cloud
                command = f'rclone config create "{r_name}" {options[index]}'

                if (
                    config["ILIAS_DOWNLOADER_CLIENT_ID"]
                    and config["ILIAS_DOWNLOADER_CLIENT_SECRET"]
                ):
                    logging.info("Using the provided client id and client secret.")

                    command += (
                        f" --{options[index]}-client-id \"{config['ILIAS_DOWNLOADER_CLIENT_ID']}\""
                        f" --{options[index]}-client-secret \"{config['ILIAS_DOWNLOADER_CLIENT_SECRET']}\""
                    )
                else:
                    logging.warning(
                        "The drive client id and the client secret have not been set. Using defaults."
                    )
            else:
                command = "rclone config"

            # run the setup command
            subprocess.run(command, shell=True)
        else:
            quit()
    else:
        # setup is complete
        return True
