import os
import re

from fastapi import UploadFile

from .BaseController import BaseController
from .ProjectController import ProjectController
from models import ResponseSignal


class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576  # convert MB to bytes

    def validate_uploaded_file(self, file: UploadFile) -> tuple[bool, str]:
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_ALLOWED.value

        file_size = getattr(file, "size", None)
        if file_size is not None and file_size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_VALIDATED_SUCCESSFULLY.value

    def generate_unique_filepath(self, filename: str, project_id: str) -> str:
        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id)
        clean_filename = self.get_clean_filename(filename)
        new_file_path = os.path.join(project_path, f"{random_key}_{clean_filename}")
        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(project_path, f"{random_key}_{clean_filename}")
        return new_file_path, f"{random_key}_{clean_filename}"

    def get_clean_filename(self, orig_filename: str):
        clean_filename = re.sub(r"[^\w.]", "", orig_filename)
        clean_filename = clean_filename.replace(" ", "_")
        return clean_filename