from django.contrib import admin
from .models import Sports, Match, MatchDay, ScheduledMatches, Team, Player


class SportsAdmin(admin.ModelAdmin):
    fields = ["name"]


class MatchAdmin(admin.ModelAdmin):
    fields = [field.name for field in Match._meta.get_fields()]
    fields.remove("id")
    fields.remove("red_ace_out")
    fields.remove("blue_ace_out")
    fields.remove("ace_out_time")
    fields.remove("swap_position")
    fields.remove("client_os")
    fields.remove("name")
    fields.remove("current_inning")

    list_filter = ("active",)

    class Meta:
        ordering = ["-date"]


class EndedMatchesAdmin(admin.ModelAdmin):
    fields = [field.name for field in Match._meta.get_fields()]
    fields.remove("id")
    fields.remove("active_set")
    fields.remove("swap_position")
    fields.remove("client_os")
    fields.remove("current_inning")
    fields.remove("ace_out_time")
    fields.remove("red_ace_out")
    fields.remove("blue_ace_out")
    fields.remove("active")


    class Meta:
        ordering = ["-date"]


class MatchDayAdmin(admin.ModelAdmin):
    fields = ["day"]

    class Meta:
        ordering = ["-day"]


class ScheduledMatchesAdmin(admin.ModelAdmin):
    fields = [field.name for field in ScheduledMatches._meta.get_fields()]
    fields.remove("id")

    class Meta:
        ordering = ["-time"]


admin.site.register(Sports, SportsAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(ScheduledMatches, ScheduledMatchesAdmin)
admin.site.register(MatchDay, MatchDayAdmin)
admin.site.register(Team)
admin.site.register(Player)
