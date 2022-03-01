from django.db import models


class Sports(models.Model):
    name = models.CharField(verbose_name="Название", max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Спорт"
        verbose_name_plural = "Виды спорта"


class Match(models.Model):
    sport = models.ForeignKey(Sports, on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name="Дата и время матча")

    def __str__(self):
        return str(self.date)

    class Meta:
        verbose_name = "Матч"
        verbose_name_plural = "Матчи"
