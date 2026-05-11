from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def home(request):
    return JsonResponse(
        {
            "status": "success",
            "message": "QueueWise API is running",
        }
    )


urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path("api/v1/", include("queues.urls")),
]