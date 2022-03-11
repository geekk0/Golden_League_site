from django.urls import path, include
from sport_site import views
urlpatterns = [
    path('', views.main),
    path('<str:sport_name>/Матч', views.enter_match, name="Матч"),
    path("Регистрация команд/<str:sport_name>", views.SquadRegister.as_view(), name="Регистрация команд"),
    path("save_data/<int:match_id>", views.match_score_save, name="save_data"),
    path("Завершение матча", views.end_match, name="Завершение матча"),
    path("Статистика/<int:match_id>", views.statistic_view, name="Статистика")
]