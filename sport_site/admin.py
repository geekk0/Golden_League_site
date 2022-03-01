from django.contrib import admin
from .models import Sports, Match


class SportsAdmin(admin.ModelAdmin):
    fields = ["name"]


class MatchAdmin(admin.ModelAdmin):
    fields = ["sport", "date"]


admin.site.register(Sports, SportsAdmin)
admin.site.register(Match, MatchAdmin)