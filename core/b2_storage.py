from b2sdk.v2 import InMemoryAccountInfo, B2Api
from django.conf import settings
from django.core.files.storage import Storage
import os


class BackblazeB2Storage(Storage):
    def __init__(self, *args, **kwargs):
        self.bucket_name = settings.B2_BUCKET_NAME
        self.application_key_id = settings.B2_KEY_ID
        self.application_key = settings.B2_APP_KEY
        self.location = kwargs.get("location", "")
        self.b2_api = B2Api(InMemoryAccountInfo())
        self.b2_api.authorize_account(
            "production", self.application_key_id, self.application_key
        )
        self.bucket = self.b2_api.get_bucket_by_name(self.bucket_name)

    def _save(self, name, content):
        content.open()
        self.bucket.upload_bytes(content.read(), name.replace("\\", "/"))
        content.close()
        return name

    def _open(self, name, mode="rb"):
        file_info = self.bucket.download_file_by_name(name.replace("\\", "/"))
        return file_info.download_to_bytes()

    def exists(self, name):
        try:
            self.bucket.get_file_info_by_name(name.replace("\\", "/"))
            return True
        except:
            return False

    def generate_filename(self, filename):
        return os.path.join(self.location, filename).replace("\\", "/")

    def url(self, name):
        download_url = "https://f005.backblazeb2.com/file"
        return f"{download_url}/{self.bucket_name}/{name.replace('\\','/')}"
