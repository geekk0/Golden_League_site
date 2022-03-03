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
    date = models.DateField(verbose_name="Дата матча", default=datetime.date.today)
    red_squad = models.CharField(verbose_name="Состав красной команды",  max_length=128)
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

    def __str__(self):
        return str(self.date)

    class Meta:
        verbose_name = "Матч"
        verbose_name_plural = "Матчи"


class EndedMatches(models.Model):
    sport = models.ForeignKey(Sports, on_delete=models.CASCADE, verbose_name="Вид спорта")
    date = models.DateField(verbose_name="Дата матча", default=datetime.date.today)
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

    def __str__(self):
        return str(self.date)

    class Meta:
        verbose_name = "Сыгранный матч"
        verbose_name_plural = "Сыгранные матчи"
