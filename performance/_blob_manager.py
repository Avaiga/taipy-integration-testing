import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

class _BlobManager:


    AZURE_STORAGE_ACCOUNT_URL = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
    AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")
    default_credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(AZURE_STORAGE_ACCOUNT_URL, credential=default_credential)


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
            with open(file=file_path, mode="wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
        else:
            if os.path.isfile(file_path):
                os.remove(file_path)


    @classmethod
    def upload_file(cls, blob_name: str, file_path: str):
        with open(file_path, mode="rb") as data:
            cls.__get_container().upload_blob(blob_name, data, overwrite=True)

