from django.urls import path, include
from sport_site import views
urlpatterns = [
    path('', views.main),
    path('beach volleyball', views.SquadRegister.as_view(), name="beach volleyball")
]