# middleware.py

from django.core.files.uploadhandler import TemporaryFileUploadHandler

class SetUploadHandlersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST':
            request.upload_handlers.insert(0, TemporaryFileUploadHandler())
        response = self.get_response(request)
        return response
