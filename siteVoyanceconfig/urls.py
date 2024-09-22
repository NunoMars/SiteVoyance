from django.contrib import admin
from django.urls import path, include, re_path
from clairvoyance.consumers import ClairvoyanteConsumer
from clairvoyance.views import IndexView, contacts
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path("admin", admin.site.urls, name="admin"),
    path("accounts/", include("accounts.urls")),
    path("clairvoyance/", include("clairvoyance.urls")),
    path("responses/", include("responses.urls")),
    path("ball8/", include("ball8.urls")),
    path("contacts", contacts, name="contacts"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if "rosetta" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^rosetta/", include("rosetta.urls"))]

websocket_urlpatterns = [
    re_path(r"ws/clairvoyante/$", ClairvoyanteConsumer.as_asgi()),
]
