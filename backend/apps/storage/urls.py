from django.urls import path

from .views import PresignUploadView, PublicUrlView

urlpatterns = [
    path("upload/presign/", PresignUploadView.as_view(), name="upload-presign"),
    path("upload/public-url/", PublicUrlView.as_view(), name="upload-public-url"),
]
