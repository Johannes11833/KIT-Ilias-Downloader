import json
import os
from pathlib import Path
from typing import List, Dict

from cloud.google_drive import GDrive


class CloudUploader:
    F_NAME_SYNC_DICT = './data/sync_dict.json'

    def __init__(self, logger, cloud_service=GDrive) -> None:
        super().__init__()

        self.logger = logger

        # set up the uploader
        self.cloud = cloud_service(logger)
        self.cloud.setup()

        # get the sync dict
        self.sync_dict: Dict
        if os.path.exists(self.F_NAME_SYNC_DICT):
            with open(self.F_NAME_SYNC_DICT) as json_file:
                self.sync_dict = json.load(json_file)
        else:
            self.sync_dict = {
                'synced_files': []
            }

    def upload_new_files(self, output_path):
        local_files = self.__get_local_file_list(Path('./output'))
        uploaded_files = self.sync_dict.get('synced_files', [])
        new_files: List[Path] = [Path(p) for p in set(local_files).difference(uploaded_files)]

        if len(new_files) > 0:
            self.cloud.upload_files(new_files, output_path)

            # update sync dict and save it as json
            self.sync_dict['synced_files'].extend([path.__str__() for path in new_files])
            with open(self.F_NAME_SYNC_DICT, 'w') as fp:
                json.dump(self.sync_dict, fp, indent='\t')
        else:
            self.logger.info('There are no new files to upload to the cloud.')

    @staticmethod
    def __get_local_file_list(path: Path) -> List:
        filelist = []

        for root, dirs, files in os.walk(path):
            for file in files:
                # append the file name to the list
                filelist.append(os.path.join(root, file))
        return filelist
