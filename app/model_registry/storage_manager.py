from __future__ import annotations

import os.path
from pathlib import Path
from typing import Final

from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
from logger.logger import ColorLogger  # noreorder # noqa


class GCloudStorageManager:
    """
    A class to manage file storage operations in Google Cloud Storage.

    This class provides methods to handle file uploads, downloads, and other storage
    operations using the Google Cloud Storage API. It initializes the storage client
    and bucket using service account credentials.

    Returns:
        GCloudStorageManager: An instance of the GCloudStorageManager class.
    """

    MODEL_BUCKET_NAME: Final = "interview_bucket"
    PROJECT_NAME: Final = "MY First Project"
    credentials_dict: Final = {  # Should be in environment file but for easy access it is in here.
        # ADD YOUR GOOGLE DRIVE CREDENTIALS !
    }

    def __init__(self, logger: ColorLogger, bucket_name: str | None = None):
        """
        Initialize the GCloudStorageManager with Google Cloud Storage client and bucket.

        This method sets up the Google Cloud Storage client and accesses the specified bucket
        using service account credentials loaded from a dictionary. It is essential that the
        `credentials_dict`, `PROJECT_NAME`, and `MODEL_BUCKET_NAME` are correctly defined
        as class-level constants.

        Raises:
            google.auth.exceptions.DefaultCredentialsError: If there is an issue with the provided credentials.
        """
        bucket_name = GCloudStorageManager.MODEL_BUCKET_NAME if bucket_name is None else bucket_name
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(GCloudStorageManager.credentials_dict)
        self.client = storage.Client(credentials=credentials, project=GCloudStorageManager.PROJECT_NAME)
        self.bucket = self.client.get_bucket(bucket_name)
        self.logger = logger

    def upload_file(self, source_filename: str, destination_filename: str):
        """
        Upload a file to Google Cloud Storage.

        This method uploads a file from the local file system to the specified destination
        in a Google Cloud Storage bucket. It uses the `blob.upload_from_filename()` method
        to perform the upload.

        Args:
            source_filename (str): The local path to the source file to be uploaded.
            destination_filename (str): The destination path in the Google Cloud Storage bucket where the file will be stored.

        Returns:
            bool: True if the file was uploaded successfully, False otherwise.
        """
        if not os.path.exists(source_filename):
            raise FileNotFoundError(f"Model file '{source_filename}' does not exist! Please check the file location.")
        try:
            blob = self.bucket.blob(destination_filename)
            blob.upload_from_filename(source_filename)
            self.logger.storage(f"File {source_filename} successfully uploaded.")
            return True
        except Exception as e:
            self.logger.storage_error(f"Exception {e}. File {source_filename} upload failed.")
            return False

    def download_file(self, filename: str, download_path: str = "Downloads"):
        """
        Download a file from Google Cloud Storage to a local directory.

        This method downloads a file from the Google Cloud Storage bucket to the specified
        local directory. If the directory does not exist, it creates it.

        Args:
            filename (str): The name of the file in the Google Cloud Storage bucket to be downloaded.
            download_path (str, optional): The local directory where the file will be downloaded.
                Defaults to "Downloads".

        Returns:
            None
        """
        try:
            if Path(download_path).suffix or download_path == "":
                self.logger.warning(f"{download_path} is likely intended to be a file.")
                download_path = "Downloads"

            os.makedirs(download_path, exist_ok=True)
            blob = self.bucket.blob(filename)
            blob.download_to_filename(download_path + os.sep + filename)  # Download the file to a destination
            message = f"File {filename} downloaded to {download_path}"
            self.logger.storage(f"File {filename} downloaded to {download_path}")
            return True, message
        except Exception as e:
            message = f"Exception {e}. File {filename} could not downloaded to {download_path}"
            self.logger.storage_error(message)
            return False, message

    def delete_file(self, destination_filename: str):
        """
        Delete a file from Google Cloud Storage.

        This method deletes a file from the Google Cloud Storage bucket. It attempts to delete
        the specified file and returns a boolean indicating whether the deletion was successful.

        Args:
            destination_filename (str): The name of the file in the Google Cloud Storage bucket to be deleted.

        Returns:
            bool: True if the file was deleted successfully, False otherwise.
        """
        try:
            blob = self.bucket.blob(destination_filename)
            blob.delete()
            self.logger.storage(f"File {destination_filename} removed successfully.")
            return True
        except Exception as e:
            self.logger.storage_error(f"File {destination_filename} could not removed. Exception {e}")
            return False
