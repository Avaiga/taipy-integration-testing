# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


class _BlobManager:
    AZURE_STORAGE_ACCOUNT_URL = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
    AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")
    default_credential = DefaultAzureCredential() if AZURE_STORAGE_ACCOUNT_URL else None
    blob_service_client = (
        BlobServiceClient(AZURE_STORAGE_ACCOUNT_URL, credential=default_credential)
        if AZURE_STORAGE_ACCOUNT_URL
        else None
    )

    @classmethod
    def __get_container(cls):
        if not hasattr(cls, "container_client"):
            cls.container_client = cls.blob_service_client.get_container_client(cls.AZURE_CONTAINER_NAME)
            if not cls.container_client.exists():
                cls.container_client = cls.blob_service_client.create_container(cls.AZURE_CONTAINER_NAME)
        return cls.container_client

    @classmethod
    def download_file(cls, blob_name: str, file_path: str):
        blob_client = cls.__get_container().get_blob_client(blob_name)
        if blob_client.exists():
            with open(file=file_path, mode="wb") as downloaded_file:
                downloaded_file.write(blob_client.download_blob().readall())
        else:
            if os.path.isfile(file_path):
                os.remove(file_path)

    @classmethod
    def upload_file(cls, blob_name: str, file_path: str):
        with open(file_path, mode="rb") as data:
            cls.__get_container().upload_blob(blob_name, data, overwrite=True)
