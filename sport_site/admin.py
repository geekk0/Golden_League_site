from django.contrib import admin
from .models import Sports, Match


class SportsAdmin(admin.ModelAdmin):
    fields = ["name"]


class MatchAdmin(admin.ModelAdmin):
    fields = [field.name for field in Match._meta.get_fields()]
    fields.remove("id")

admin.site.register(Sports, SportsAdmin)
admin.site.register(Match, MatchAdmin)