from dataclasses import dataclass
from typing import Iterator, Optional

from dataclasses_json import dataclass_json


@dataclass
class OSSConfig:
    access_key_id: str
    access_key_secret: str
    security_token: Optional[str] = None
    region: Optional[str] = "cn-shanghai"
    endpoint: Optional[str] = None
    oss_concurrency_limit: Optional[int] = 500


@dataclass
class OSSDownloadResults:
    files: Iterator
    time: float


@dataclass
class OSSDownloadFolderResults:
    num_of_files: int
    time: float


@dataclass_json
@dataclass
class OSSUploadResults:
    num_of_files: int
    time: float


@dataclass_json
@dataclass
class OSSUploadObject:
    key: str
    data: bytes


@dataclass_json
@dataclass
class OSSPath:
    bucket: str
    key: str


@dataclass_json
@dataclass
class OSSDownloadRequest(OSSPath):
    process: Optional[str] = None
    headers: Optional[dict] = None
    params: Optional[dict] = None


@dataclass_json
@dataclass
class OSSSignRequest(OSSPath):
    expires: Optional[int] = 36000
    process: Optional[str] = None
    headers: Optional[dict] = None
    params: Optional[dict] = None


@dataclass_json
@dataclass
class _OSSSessionAuth:
    access_key_id: str
    access_key_secret: str
    security_token: Optional[str] = None


@dataclass_json
@dataclass
class _OSSSessionConf:
    region: str
    endpoint: str
    oss_concurrency_limit: int


@dataclass_json
@dataclass
class _OSSUtilFlags:
    credentials: str
    endpoint: str
    extra_flags: str
