from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse


def healthcheck(request):
    return HttpResponse("OK", status=200)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('form.urls')),
    path("healthz/", healthcheck),
]
