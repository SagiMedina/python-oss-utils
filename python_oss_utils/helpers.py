import os
import subprocess
from pathlib import Path
from typing import Optional

import oss2
from oss2 import Bucket
from oss2.models import ListObjectsV2Result

from python_oss_utils.models import OSSDownloadRequest, OSSConfig, _OSSSessionAuth, _OSSSessionConf, OSSPath, \
    OSSSignRequest, _OSSUtilFlags

OSS_UTIL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "ossutil"))


def parse_oss_path(oss_path: str) -> OSSPath:
    bucket, key = oss_path.lstrip("oss://").split("/", 1)
    return OSSPath(bucket=bucket, key=key)


class _OSSSession:

    def __init__(self, config: OSSConfig):
        self.session_auth = _OSSSessionAuth(
            access_key_id=config.access_key_id,
            access_key_secret=config.access_key_secret,
            security_token=config.security_token
        )
        self.session_conf = _OSSSessionConf(
            region=OSSConfig.region,
            endpoint=f"http://oss-{OSSConfig.region}.aliyuncs.com"
            if OSSConfig.endpoint is None
            else OSSConfig.endpoint,
            oss_concurrency_limit=OSSConfig.oss_concurrency_limit,
        )
        self.session_buckets = {}

    def get_oss_auth_instance(self):
        if self.session_auth.security_token:
            return oss2.StsAuth(access_key_id=self.session_auth.access_key_id,
                                access_key_secret=self.session_auth.access_key_secret,
                                security_token=self.session_auth.security_token)

        return oss2.AuthV2(access_key_id=self.session_auth.access_key_id,
                           access_key_secret=self.session_auth.access_key_secret)

    def create_oss_bucket_api(self, bucket: str) -> Bucket:
        if bucket in self.session_buckets:
            return self.session_buckets.get(bucket)
        oss_session = oss2.Session()
        oss_auth = self.get_oss_auth_instance()
        # noinspection PyTypeChecker
        oss_bucket_api = oss2.Bucket(oss_auth, self.session_conf.endpoint, bucket, session=oss_session)
        self.session_buckets[bucket] = oss_bucket_api
        return oss_bucket_api

    def sign_file_url(self, oss_sign_request: OSSSignRequest):
        oss_client = self.create_oss_bucket_api(oss_sign_request.bucket)
        oss_request = {
            "headers": oss_sign_request.headers,
            "params": oss_sign_request.params or {},
        }
        if oss_sign_request.process:
            oss_request["params"].update({"x-oss-process": oss_sign_request.process})
        return oss_client.sign_url("GET", oss_sign_request.key, oss_sign_request.expires, **oss_request)

    def get_nested_files_list_from_oss_dir(self, oss_dir_path, next_continuation_token='', nested_files_list=None):
        if nested_files_list is None:
            nested_files_list = []
        oss_path = parse_oss_path(oss_dir_path)
        oss_client = self.create_oss_bucket_api(oss_path.bucket)
        bucket_content: ListObjectsV2Result = oss_client.list_objects_v2(oss_path.key, continuation_token=next_continuation_token, max_keys=1000)
        nested_files_list.extend([f"oss://{oss_path.bucket}/{oss_object.key}" for oss_object in bucket_content.object_list if not oss_object.key.endswith('/')])
        if bucket_content.next_continuation_token != '':
            self.get_nested_files_list_from_oss_dir(oss_dir_path, bucket_content.next_continuation_token, nested_files_list)
        return nested_files_list

    def download_file(self, oss_download_request: OSSDownloadRequest, download_to_folder: Optional[str]):
        oss_client = self.create_oss_bucket_api(oss_download_request.bucket)
        oss_request = {
            "headers": oss_download_request.headers,
            "process": oss_download_request.process,
            "params": oss_download_request.params,
        }
        if download_to_folder:
            Path(download_to_folder).mkdir(parents=True, exist_ok=True)
            file_name = os.path.basename(oss_download_request.key)
            file_in_cache = os.path.join(download_to_folder, file_name)
            if not os.path.exists(file_in_cache):
                oss_client.get_object_to_file(oss_download_request.key, filename=file_in_cache, **oss_request)
            file_bytes = Path(file_in_cache).read_bytes()
            if len(file_bytes) > 0:
                return file_bytes

        try:
            file = oss_client.get_object(oss_download_request.key, **oss_request)
        except oss2.exceptions.ServerError:
            return None

        return file.read()

    def get_oss_util_flags(self) -> _OSSUtilFlags:
        credentials = f"--access-key-id={self.session_auth.access_key_id} --access-key-secret={self.session_auth.access_key_secret}"
        if self.session_auth.security_token:
            credentials = f"{credentials} --sts-token={self.session_auth.security_token}"
        endpoint = f"--endpoint={self.session_conf.endpoint}"
        flags = f"--recursive --update --jobs={self.session_conf.oss_concurrency_limit}"
        return _OSSUtilFlags(credentials=credentials, endpoint=endpoint, extra_flags=flags)

    def upload_with_oss_util(self, oss_path: str, local_upload_folder_path: str):
        oss_util_flags = self.get_oss_util_flags()
        cmd = f"{OSS_UTIL_PATH} cp {local_upload_folder_path} {oss_path.rstrip('/')} {oss_util_flags.credentials} {oss_util_flags.endpoint} {oss_util_flags.extra_flags}"
        popen = subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        popen.wait()

    def download_with_oss_util(self, oss_path: str, local_download_folder_path: str):
        oss_util_flags = self.get_oss_util_flags()
        cmd = f"{OSS_UTIL_PATH} cp {oss_path.rstrip('/')} {local_download_folder_path} {oss_util_flags.credentials} {oss_util_flags.endpoint} {oss_util_flags.extra_flags}"
        popen = subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        popen.wait()

    def upload_file(self, bucket, file_upload_path, file_data):
        oss_client = self.create_oss_bucket_api(bucket)
        return oss_client.put_object(file_upload_path, file_data)
