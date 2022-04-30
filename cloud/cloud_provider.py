from abc import ABC, abstractmethod
from pathlib import Path
from typing import List


class CloudProvider(ABC):
    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def upload_files(self, files: List, output_path: Path):
        pass
