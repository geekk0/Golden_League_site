import time
import datetime

from django.db import models



class Sports(models.Model):
    name = models.CharField(verbose_name="Название", max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Спорт"
        verbose_name_plural = "Виды спорта"


class Match(models.Model):
    sport = models.ForeignKey(Sports, on_delete=models.CASCADE, verbose_name="Вид спорта")
    date = models.DateTimeField(verbose_name="Дата матча", null=True, blank=True)
    active = models.CharField(verbose_name="Активный/Завершенный", default="Завершенный", max_length=128)
    name = models.CharField(verbose_name="Название матча", max_length=128, null=True, blank=True)
    red_squad = models.CharField(verbose_name="Состав красной команды",  max_length=10)
    blue_squad = models.CharField(verbose_name="Состав синей команды",  max_length=10)
    red_set_score = models.IntegerField(verbose_name="Выигранные партии красной команды", default=0)
    blue_set_score = models.IntegerField(verbose_name="Выигранные партии синей команды", default=0)
    red_points_set_1 = models.IntegerField(verbose_name="Очки красных в 1 партии", default=0)
    red_points_set_2 = models.IntegerField(verbose_name="Очки красных во 2 партии", default=0)
    red_points_set_3 = models.IntegerField(verbose_name="Очки красных в 3 партии", default=0)
    blue_points_set_1 = models.IntegerField(verbose_name="Очки синих в 1 партии", default=0)
    blue_points_set_2 = models.IntegerField(verbose_name="Очки синих во 2 партии", default=0)
    blue_points_set_3 = models.IntegerField(verbose_name="Очки синих в 3 партии", default=0)
    active_set = models.IntegerField(verbose_name="Текущая партия", default=1)
    current_inning = models.CharField(verbose_name="Текущая подача",  max_length=128, default="blank")
    client_os = models.CharField(verbose_name="ОС клиента",  max_length=128, default="common")
    swap_position = models.IntegerField(verbose_name="Позиция кнопок", default=1)
    total_current_set = models.IntegerField(verbose_name="Тотал текущей партии", default=0)
    red_team_total = models.IntegerField(verbose_name="Тотал красной команды", default=0)
    blue_team_total = models.IntegerField(verbose_name="Тотал синей команды", default=0)
    match_total = models.IntegerField(verbose_name="Тотал матча", default=0)
    red_ace_out = models.CharField(verbose_name="Ace/out красных", default=" ", max_length=10, null=True)
    blue_ace_out = models.CharField(verbose_name="Ace/out синих", default=" ", max_length=10, null=True)
    ace_out_time = models.DateTimeField(verbose_name="Время ace/out", null=True)

    inning_points_1 = models.CharField(verbose_name="Очки подач 1 сет", null=True, blank=True, max_length=1024,
                                       default="")
    inning_points_2 = models.CharField(verbose_name="Очки подач 2 сет", null=True, blank=True, max_length=1024,
                                       default="")
    inning_points_3 = models.CharField(verbose_name="Очки подач 3 сет", null=True, blank=True, max_length=1024,
                                       default="")

    def __str__(self):
        return str(self.date.strftime("%d.%m.%y %H:%M ")) + self.red_squad + " - " + self.blue_squad \
            + " (" + str(self.id) + ")"

    def get_name(self):
        self.name = str(self.date.strftime("%d.%m.%y %H:%M ")) + self.red_squad + " - " + self.blue_squad \
            + " (" + str(self.id) + ")"

    class Meta:
        verbose_name = "Матч"
        verbose_name_plural = "Матчи"


class EndedMatches(models.Model):
    sport = models.ForeignKey(Sports, on_delete=models.CASCADE, verbose_name="Вид спорта")
    date = models.DateTimeField(verbose_name="Дата матча", null=True, blank=True)
    name = models.CharField(verbose_name="Название матча", max_length=128, null=True, blank=True)
    red_squad = models.CharField(verbose_name="Состав красной команды", max_length=128)
    blue_squad = models.CharField(verbose_name="Состав синей команды",  max_length=128)
    red_set_score = models.IntegerField(verbose_name="Выигранные партии красной команды", default=0)
    blue_set_score = models.IntegerField(verbose_name="Выигранные партии синей команды", default=0)
    red_points_set_1 = models.IntegerField(verbose_name="Очки красных в 1 партии", default=0)
    red_points_set_2 = models.IntegerField(verbose_name="Очки красных во 2 партии", default=0)
    red_points_set_3 = models.IntegerField(verbose_name="Очки красных в 3 партии", default=0)
    blue_points_set_1 = models.IntegerField(verbose_name="Очки синих в 1 партии", default=0)
    blue_points_set_2 = models.IntegerField(verbose_name="Очки синих во 2 партии", default=0)
    blue_points_set_3 = models.IntegerField(verbose_name="Очки синих в 3 партии", default=0)
    active_set = models.IntegerField(verbose_name="Текущая партия", default=1)
    total_current_set = models.IntegerField(verbose_name="Тотал текущей партии", default=0)
    red_team_total = models.IntegerField(verbose_name="Тотал красной команды", default=0)
    blue_team_total = models.IntegerField(verbose_name="Тотал синей команды", default=0)
    match_total = models.IntegerField(verbose_name="Тотал матча", default=0)
    inning_points_1 = models.CharField(verbose_name="Очки подач 1 сет", null=True, blank=True, max_length=1024,
                                       default="")
    inning_points_2 = models.CharField(verbose_name="Очки подач 2 сет", null=True, blank=True, max_length=1024,
                                       default="")
    inning_points_3 = models.CharField(verbose_name="Очки подач 3 сет", null=True, blank=True, max_length=1024,
                                       default="")

    def __str__(self):
        return str(self.date.strftime("%d.%m.%y %H:%M ")) + self.red_squad + " - " + self.blue_squad \
               + " (" + str(self.id) + ")"

    def get_name(self):
        self.name = str(self.date.strftime("%d.%m.%y %H:%M ")) + self.red_squad + " - " + self.blue_squad \
            + " (" + str(self.id) + ")"

    class Meta:
        verbose_name = "Сыгранный матч"
        verbose_name_plural = "Сыгранные матчи"
