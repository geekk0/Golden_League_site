from django.urls import path, include
from sport_site import views
urlpatterns = [
    path('', views.main),
    path('<str:sport_name>/Матч', views.enter_match, name="Матч"),
    path("Регистрация команд", views.SquadRegister.as_view(), name="Регистрация команд"),
    path("save_data/<int:match_id>", views.match_score_save, name="save_data")
]