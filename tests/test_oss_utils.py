import os
import unittest

from python_oss_utils.helpers import parse_oss_path, OSS_UTIL_PATH
from python_oss_utils.models import OSSConfig, OSSSignRequest, OSSDownloadRequest
from python_oss_utils.oss_utils import OSSUtils

TEST_FILE = 'oss://miil-pc-sh/datasets/tmp/test/example_imm.jpeg'
TEST_FOLDER = 'oss://miil-pc-sh/datasets/tmp/test/'
LOCAL_DOWNLOAD_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "downloads")


@unittest.skip("Need to fix Auth keys on Jenkins")
class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config = OSSConfig(
            access_key_id=os.getenv("ALIYUN_ACCESS_KEY"),
            access_key_secret=os.getenv("ALIYUN_SECRET_KEY"),
        )
        cls.oss_utils = OSSUtils(config)

    def test_sign_url(self):
        url = self.oss_utils.sign_file_url(TEST_FILE)
        assert type(url) == str

    def test_sign_url_with_request(self):
        oss_path = parse_oss_path(TEST_FILE)
        sign_request = OSSSignRequest(
            bucket=oss_path.bucket,
            key=oss_path.key,
            process=f'image/resize,h_300'
        )
        url = self.oss_utils.sign_file_url(sign_request)
        assert type(url) == str

    def test_download_files(self):
        res = self.oss_utils.download_files([TEST_FILE])
        assert len(list(res.files)) == 1

    def test_download_files_with_request(self):
        oss_path = parse_oss_path(TEST_FILE)
        download_request = OSSDownloadRequest(
            bucket=oss_path.bucket,
            key=oss_path.key,
            process=f'image/resize,h_300'
        )
        res = self.oss_utils.download_files([download_request])
        assert len(list(res.files)) == 1

    def test_download_folder(self):
        os.rename(OSS_UTIL_PATH, f"{OSS_UTIL_PATH}_temp")
        res = self.oss_utils.download_folder(TEST_FOLDER, LOCAL_DOWNLOAD_PATH)
        assert res.num_of_files > 0
        os.rename(f"{OSS_UTIL_PATH}_temp", OSS_UTIL_PATH)

    def test_upload_folder(self):
        os.rename(OSS_UTIL_PATH, f"{OSS_UTIL_PATH}_temp")
        self.oss_utils.download_folder(TEST_FOLDER, LOCAL_DOWNLOAD_PATH)
        res = self.oss_utils.upload_folder_content(TEST_FOLDER, LOCAL_DOWNLOAD_PATH)
        assert res.num_of_files > 0
        os.rename(f"{OSS_UTIL_PATH}_temp", OSS_UTIL_PATH)
        oss_path = parse_oss_path(TEST_FOLDER)
        uploaded_files = self.oss_utils.get_nested_files_list_from_oss_dir(f"{TEST_FOLDER}datasets")
        self.oss_utils.get_bucket_session(oss_path.bucket).batch_delete_objects(
            [parse_oss_path(upfile).key for upfile in uploaded_files])

    def test_download_folder_with_ossutil(self):
        res = self.oss_utils.download_folder(TEST_FOLDER, LOCAL_DOWNLOAD_PATH)
        assert res.num_of_files > 0

    def test_upload_folder_with_ossutil(self):
        self.oss_utils.download_folder(TEST_FOLDER, LOCAL_DOWNLOAD_PATH)
        res = self.oss_utils.upload_folder_content(TEST_FOLDER, LOCAL_DOWNLOAD_PATH)
        assert res.num_of_files > 0
        oss_path = parse_oss_path(TEST_FOLDER)
        uploaded_files = self.oss_utils.get_nested_files_list_from_oss_dir(f"{TEST_FOLDER}datasets")
        self.oss_utils.get_bucket_session(oss_path.bucket).batch_delete_objects(
            [parse_oss_path(upfile).key for upfile in uploaded_files])


if __name__ == '__main__':
    unittest.main()
