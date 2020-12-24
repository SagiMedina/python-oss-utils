import concurrent.futures
import os
import time
from pathlib import Path
from typing import List, Union, Optional

from python_oss_utils.helpers import _OSSSession, OSS_UTIL_PATH, parse_oss_path
from python_oss_utils.models import OSSConfig, OSSDownloadRequest, OSSDownloadResults, \
    OSSUploadResults, OSSUploadObject, OSSSignRequest, OSSDownloadFolderResults
from python_oss_utils.utils import get_content_folder_list


class OSSUtils:
    def __init__(self, config: OSSConfig):
        self.oss_session = _OSSSession(config)

    def sign_file_url(self, oss_path_to_sign: Union[str, OSSSignRequest]):
        oss_sign_request = oss_path_to_sign
        if not isinstance(oss_path_to_sign, OSSSignRequest):
            oss_path = parse_oss_path(oss_path_to_sign)
            oss_sign_request = OSSSignRequest(**oss_path.to_dict())
        return self.oss_session.sign_file_url(oss_sign_request)

    def download_files(self, oss_paths: List[Union[str, OSSDownloadRequest]], download_to_folder: Optional[str] = None, keep_folders_struct: Optional[bool] = False) -> OSSDownloadResults:
        start = time.time()
        downloader = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for oss_download_request in oss_paths:
                if not isinstance(oss_download_request, OSSDownloadRequest):
                    oss_path = parse_oss_path(oss_download_request)
                    oss_download_request = OSSDownloadRequest(**oss_path.to_dict())
                if os.path.basename(oss_download_request.key) == '':
                    continue
                download_path = download_to_folder
                if download_to_folder and keep_folders_struct:
                    download_path = os.path.join(download_path, os.path.dirname(oss_download_request.key))
                downloader.append((oss_download_request, download_path))
            files = executor.map(lambda args: self.oss_session.download_file(*args), downloader)
            return OSSDownloadResults(files=files, time=time.time() - start)

    def download_folder(self, oss_path: str, local_download_folder_path: str) -> OSSDownloadFolderResults:
        start = time.time()
        if os.path.exists(OSS_UTIL_PATH):
            self.oss_session.download_with_oss_util(oss_path, local_download_folder_path)
        else:
            nested_files_list = self.oss_session.get_nested_files_list_from_oss_dir(oss_path)
            if not nested_files_list:
                return OSSDownloadFolderResults(num_of_files=0, time=time.time() - start)
            self.download_files(oss_paths=nested_files_list, download_to_folder=local_download_folder_path, keep_folders_struct=True)
        return OSSDownloadFolderResults(num_of_files=sum([len(files) for r, d, files in os.walk(local_download_folder_path)]),
                                        time=time.time() - start)

    def upload_folder_content(self, oss_path: str, local_upload_folder_path: str) -> OSSUploadResults:
        if os.path.exists(OSS_UTIL_PATH):
            start = time.time()
            self.oss_session.upload_with_oss_util(oss_path, local_upload_folder_path)
            return OSSUploadResults(num_of_files=len(os.listdir(local_upload_folder_path)), time=time.time() - start)
        return self.upload_files(oss_path,
                                 [OSSUploadObject(key=file, data=Path(os.path.join(local_upload_folder_path, file)).read_bytes()) for
                                  file in get_content_folder_list(local_upload_folder_path)])

    def upload_files(self, upload_path: str, files_to_upload: List[OSSUploadObject]) -> OSSUploadResults:
        start = time.time()
        uploader = []
        oss_path = parse_oss_path(upload_path)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for file in files_to_upload:
                file_upload_path = f"{oss_path.key.rstrip('/')}/{file.key}"
                uploader.append(executor.submit(self.oss_session.upload_file, oss_path.bucket, file_upload_path, file.data))
            return OSSUploadResults(num_of_files=len(files_to_upload), time=time.time() - start)
