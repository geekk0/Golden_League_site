from django.urls import path
from api.beach_volleyball import views

urlpatterns = [
    path('/Узнать счет', views.GetMatchData.as_view({'get': 'list'})),
]
