from pathlib import Path
from typing import List

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from tqdm import tqdm

from cloud.cloud_provider import CloudProvider


class GDrive(CloudProvider):
    F_NAME_CLIENT_CREDENTIALS = './data/CLIENT_CREDENTIALS.txt'

    def __init__(self, logger, path_client_secrets='./data/client_secrets.json') -> None:
        super().__init__()

        self.logger = logger
        self.g_auth = None

        # set the path to the client config file
        GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = path_client_secrets

    def setup(self):
        g_auth = GoogleAuth()
        self.g_auth = g_auth
        # try to get credentials
        g_auth.LoadCredentialsFile(self.F_NAME_CLIENT_CREDENTIALS)

        if g_auth.credentials is None:
            # Hopefully this solves the refreshing issues:
            g_auth.GetFlow()
            g_auth.flow.params.update({'access_type': 'offline'})
            g_auth.flow.params.update({'approval_prompt': 'force'})

            g_auth.LocalWebserverAuth()
        elif g_auth.access_token_expired:
            self.logger.info('Refreshing access token')
            # Refresh them if expired
            g_auth.Refresh()
        else:
            # Initialize the saved credentials
            g_auth.Authorize()

        # Save the current credentials to a file
        g_auth.SaveCredentialsFile(self.F_NAME_CLIENT_CREDENTIALS)

        self.logger.info('Initial setup of the backup service completed')

    def upload_files(self, files: List[Path], output_path: Path):
        drive = GoogleDrive(self.g_auth)
        drive_folder_name_output = Path(output_path)

        # get the id of the folder that we want to upload to
        upload_root_folder_id = self._check_create_path(drive_folder_name_output, drive)

        self.logger.info('Starting upload to google drive')
        for file_path in tqdm(files):
            self._upload_file(drive, upload_root_folder_id, file_path)
        self.logger.info('Upload completed.')

    def _check_create_path(self, path: Path, drive, root_folder_id=None):
        parts = path.parts

        if len(parts) == 0:
            # path is empty
            return
        else:
            # check if root folder already exists, otherwise create it
            parent_folder_id = self._check_create_folder(drive, parts[0], root_folder_id)

            # do the same for the remaining parts of the path
            for folder_name in parts[1:]:
                parent_folder_id = self._check_create_folder(drive, folder_name, parent_folder_id)
            return parent_folder_id

    def _check_create_folder(self, drive, folder_name, parent_folder_id) -> str:
        folder_id = None

        if parent_folder_id:
            # get folders in parent folder
            file_list = drive.ListFile({'q': f"'{parent_folder_id}' in parents and trashed=false "
                                             f"and mimeType='application/vnd.google-apps.folder'"}).GetList()
        else:
            # get folders in root (first folder in path, the parent)
            file_list = drive.ListFile({'q': "'root' in parents and trashed=false "
                                             "and mimeType='application/vnd.google-apps.folder'"}).GetList()

        # loop through folder and check if the next part of the path already exists, if not create it
        for g_file in file_list:
            if g_file['title'] == folder_name:
                folder_id = g_file['id']

        if not folder_id:
            return self._create_folder(drive, folder_name, parent_folder_id)
        else:
            return folder_id

    @staticmethod
    def _create_folder(drive, folder_name: str, parent_folder_id: str = None):
        # create the folder as it does not exist yet
        params = {'title': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}

        # add parent property
        if parent_folder_id is not None:
            params['parents'] = [{'id': parent_folder_id}]

        folder = drive.CreateFile(params)
        folder.Upload()
        folder_id = folder['id']

        return folder_id

    def _upload_file(self, drive, root_folder_id: str, file_path_in: Path):
        # the path to the file on the cloud should be the one of the in-file, without the name of the local output
        # folder
        file_path_out = Path(*file_path_in.parts[1:])

        # check if the file is in a sub-folder of the output folder or in its root
        if len(file_path_out.parts) > 1:
            folder_id = self._check_create_path(file_path_out.parent, drive, root_folder_id)
        else:
            folder_id = root_folder_id

        # check if the file already exists
        file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false "
                                         "and not mimeType='application/vnd.google-apps.folder'"}).GetList()
        for file in file_list:
            if file['title'] == file_path_out.name:
                # The file already exists, don't upload it again.
                return

        # upload the file to G-Drive
        file = drive.CreateFile(
            {'parents': [{'id': folder_id}], 'title': file_path_out.name})
        file.SetContentFile(file_path_in)
        file.Upload()
