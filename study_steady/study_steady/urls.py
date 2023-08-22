from django.contrib import admin
from django.urls import path,include

# FOR STATIC IMAGES
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include("discord.urls")),
    path('api/',include('discord.api.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    


