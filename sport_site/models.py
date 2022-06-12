import time
import datetime

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]


class Sports(models.Model):
    name = models.CharField(verbose_name="Название", max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Спорт"
        verbose_name_plural = "Виды спорта"


class Team(models.Model):
    name = models.CharField(verbose_name="Название команды", max_length=64, null=True, blank=True)
    games_played = models.IntegerField(verbose_name="Количество сыгранных матчей", default=0)
    sets_played = models.IntegerField(verbose_name="Количество сыгранных партий", default=0)
    dry_wins = models.IntegerField(verbose_name='Побед "всухую"', default=0)
    games_won = models.IntegerField(verbose_name="Количество выигранных матчей", default=0)
    total_points = models.IntegerField(verbose_name="Общее количество очков", default=0)
    win_percentage = models.IntegerField(verbose_name="% побед", default=0.0)
    sets_won = models.IntegerField(verbose_name="Количество выигранных партий", default=0)
    aces = models.IntegerField(verbose_name="Результативные подачи", default=0)
    outs = models.IntegerField(verbose_name="Ауты", default=0)

    def __str__(self):
        return self.name

    def get_win_percentage(self):
        percentage = self.games_won / self.games_played * 100
        self.win_percentage = round(percentage, 2)

    class Meta:
        verbose_name = "Команда"
        verbose_name_plural = "Команды"


class Match(models.Model):
    sport = models.ForeignKey(Sports, on_delete=models.CASCADE, verbose_name="Вид спорта")
    date = models.DateTimeField(verbose_name="Дата матча", null=True, blank=True)
    active = models.CharField(verbose_name="Активный/Завершенный", default="Завершенный", max_length=128)
    name = models.CharField(verbose_name="Название матча", max_length=128, null=True, blank=True)
    red_squad = models.CharField(verbose_name="Название красной команды",  max_length=10)
    blue_squad = models.CharField(verbose_name="Название синей команды",  max_length=10)
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
    red_team = models.ForeignKey(Team, verbose_name="Команда красных", related_name="red_team", blank=True, null=True,
                                 on_delete=models.SET_NULL)
    blue_team = models.ForeignKey(Team, verbose_name="Команда синих", related_name="blue_team", blank=True, null=True,
                                  on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.date.strftime("%d.%m.%y %H:%M ")) + self.red_squad + " - " + self.blue_squad \
            + " (" + str(self.id) + ")"

    def get_name(self):
        self.name = str(self.date.strftime("%d.%m.%y %H:%M ")) + self.red_squad + " - " + self.blue_squad \
            + " (" + str(self.id) + ")"

    class Meta:
        verbose_name = "Матч"
        verbose_name_plural = "Матчи"


class MatchDay(models.Model):
    day = models.DateField(verbose_name="Дата матча", null=True, blank=True)

    def __str__(self):
        return str(self.day)

    class Meta:
        verbose_name = "Игровой день"
        verbose_name_plural = "Игровые дни"


class ScheduledMatches(models.Model):
    day = models.ForeignKey(MatchDay, verbose_name="День", on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(verbose_name="Дата матча", null=True, blank=True)
    time = models.TimeField(verbose_name="Время матча", null=True, blank=True)
    red_team = models.CharField(verbose_name="Красная команда", null=True, blank=True, max_length=128)
    blue_team = models.CharField(verbose_name="Синяя команда", null=True, blank=True, max_length=128)

    def __str__(self):
        return str(self.time) + " " + str(self.red_team) + ":" + str(self.blue_team)

    class Meta:
        verbose_name = "Запланированный матч"
        verbose_name_plural = "Запланированные матчи"


class Player(models.Model):
    name = models.CharField(verbose_name="Имя игрока", max_length=128, null=True, blank=True)
    team = models.ManyToManyField(Team, blank=True)
    number = models.IntegerField(verbose_name="Номер", null=True, blank=True)
    games = models.IntegerField(verbose_name="Сыграно матчей", default=0)
    sets = models.IntegerField(verbose_name="Сыграно партий", default=0)
    points_total_season = models.IntegerField(verbose_name="Набрано очков", default=0)
    games_won = models.IntegerField(verbose_name="Выиграно матчей", default=0)
    innings = models.IntegerField(verbose_name="Количество подач", default=0)
    best_teammate = models.CharField(verbose_name="Лучший партнер по команде", max_length=128, default="Не определен")
    worst_teammate = models.CharField(verbose_name="Худший партнер по команде", max_length=128, default="Не определен")
    aces_total_season = models.IntegerField(verbose_name="Количество Ace", default=0)
    outs_total_season = models.IntegerField(verbose_name="Количество Out", default=0)
    current_match_points = models.IntegerField(verbose_name="Очков в текущей игре", default=0)
    current_match_innings = models.IntegerField(verbose_name="Подач в текущем матче", default=0)
    current_match_aces = models.IntegerField(verbose_name="Ace в текущем матче", default=0)
    current_match_outs = models.IntegerField(verbose_name="Out в текущем матче", default=0)
    inning = models.CharField(verbose_name="Очередность подачи в текущем матче", max_length=128, default="False")

    def __str__(self):
        return self.name

    def get_best_teammate(self):
        if self.games > 0:
            team = Team.objects.filter(player=self).order_by("-win_percentage").first()
            teammate = Player.objects.filter(team=team).exclude(id=self.id).first()
            self.best_teammate = teammate.name

    def get_worst_teammate(self):
        if self.games > 0:
            team = Team.objects.filter(player=self).order_by("win_percentage").first()
            teammate = Player.objects.filter(team=team).exclude(id=self.id).first()
            self.worst_teammate = teammate.name

    class Meta:
        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"








