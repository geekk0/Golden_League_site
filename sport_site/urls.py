from django.urls import path, include
from sport_site import views
urlpatterns = [
    path('', views.main),
    path('<str:sport_name>/Матч', views.enter_match, name="Матч"),
    path('sport', views.testfunc),
    path("Регистрация команд", views.SquadRegister.as_view(), name="Регистрация команд"),
    path("send_data/<int:match_id>", views.data_send, name="send_data")
]