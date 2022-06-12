from django.urls import path, include


urlpatterns = [
    path('Пляжный волейбол/', include('api.beach_volleyball.urls')),
]
