from django.urls import path, include
from sport_site import views
urlpatterns = [
    path('', views.main),
    path('<str:sport_name>/Матч', views.enter_match, name="Матч"),
    path("Регистрация команд/<str:sport_name>", views.SquadRegister.as_view(), name="Регистрация команд"),
    path("Завершение матча", views.end_match, name="Завершение матча"),
    path("Протокол/<int:match_id>", views.statistic_view, name="Протокол"),
    path("Изменить счет/<str:match_id>/<str:team>/<str:action>", views.change_points, name="Изменить счет"),
    path("Закончить партию/<int:match_id>", views.end_set, name="Закончить партию"),
    path("Подача/<int:match_id>/<str:team>", views.set_inning, name="Подача"),
    path("Поменять стороны/<int:match_id>", views.swap_controls, name="Поменять стороны"),
    path("Ace/Out/<int:match_id>/<str:team>/<str:action>", views.ace_out, name="Ace/Out"),
    path("user_logout/", views.user_logout, name="user_logout"),
    path("Закончить матч", views.end_match, name="Закончить матч"),
    path("Удалить матч/<int:match_id>", views.kill_match, name="Удалить матч")

]