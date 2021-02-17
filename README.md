# OSS SDK Wrapper
OSS SDK wrapper

## Usage

```python
import os
import sys
from pathlib import Path
from python_oss_utils.helpers import parse_oss_path
from python_oss_utils.models import OSSConfig, OSSSignRequest, OSSDownloadRequest, OSSUploadObject
from python_oss_utils.oss_utils import OSSUtils

config = OSSConfig(
    access_key_id=os.getenv("OSS_ACCESS_KEY"),
    access_key_secret=os.getenv("OSS_SECRET_KEY"),
)
oss_utils = OSSUtils(config)

# parse_oss_path
oss_path = parse_oss_path(oss_path='path')
print(oss_path.bucket)
print(oss_path.key)

# sign_url
url = oss_utils.sign_file_url(oss_path_to_sign='path')

# sign_url_with_request
oss_path = parse_oss_path(oss_path='path')
sign_request = OSSSignRequest(
    bucket=oss_path.bucket,
    key=oss_path.key,
    process=f'image/resize,h_300'
)
url = oss_utils.sign_file_url(sign_request)

# download_files
download = oss_utils.download_files(['some_oss_path', 'another_oss_path'])
for downloaded_file in download.files:
    print(sys.getsizeof(downloaded_file))
    
# download_files_with_request
files_to_download_list = ['some_oss_path', 'another_oss_path']
download_requests = []
for file_to_download in files_to_download_list:
    oss_path = parse_oss_path(file_to_download)
    download_requests.append(
        OSSDownloadRequest(
            bucket=oss_path.bucket,
            key=oss_path.key,
            process=f'image/resize,h_300'
        )
    )

download = oss_utils.download_files(download_requests)
for downloaded_file in download.files:
    print(sys.getsizeof(downloaded_file))
    
# download_and_save
oss_utils.download_files(
    oss_paths=['some_oss_path', 'another_oss_path'], 
    download_to_folder='LOCAL_DOWNLOAD_PATH',
    keep_folders_struct=True # if false => download all nested files to LOCAL_DOWNLOAD_PATH
)

# upload_files
files_path = ['path1/file1.jpg', 'path2/file2.jpg']
files_to_upload = []
for file_path in files_path:
    files_to_upload.append(
        OSSUploadObject(
            key=os.path.basename(file_path), 
            data=Path(file_path).read_bytes()
        )
    )
oss_utils.upload_files('OSS_BASE_FOLDER', files_to_upload)

# download_and_save_folder
oss_utils.download_folder('OSS_FOLDER', 'LOCAL_DOWNLOAD_PATH')

# upload folder
oss_utils.upload_folder_content('OSS_FOLDER', 'LOCAL_PATH')



```

