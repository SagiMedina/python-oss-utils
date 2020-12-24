import hashlib
import os
from pathlib import Path


def encrypt_string(hash_string) -> str:
    sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature


def get_content_folder_list(dir_path) -> list[str]:
    files_list = []
    for object_in_dir in os.walk(dir_path):
        if object_in_dir[2]:
            files_list.extend([f"{Path(object_in_dir[0]).relative_to(dir_path)}/{filename}" for filename in object_in_dir[2]])
    return files_list
