from django.contrib import admin
from django.urls import path
from waitlist.views import api  # type: ignore

urlpatterns = [
    path('admin-jiraiya/', admin.site.urls),
    path('api/', api.urls),
]
