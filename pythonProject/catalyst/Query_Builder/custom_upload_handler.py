# custom_upload_handler.py

from django.core.files.uploadhandler import TemporaryFileUploadHandler


class CustomUploadHandler(TemporaryFileUploadHandler):
    def __init__(self, request=None):
        super().__init__(request)

    def receive_data_chunk(self, raw_data, start):
        # Process each chunk here (optional)
        return super().receive_data_chunk(raw_data, start)

    def file_complete(self, file_size):
        # Called when the file is completely uploaded (optional)
        return super().file_complete(file_size)
