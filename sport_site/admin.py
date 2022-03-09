from django.contrib import admin
from .models import Sports, Match, EndedMatches


class SportsAdmin(admin.ModelAdmin):
    fields = ["name"]


class MatchAdmin(admin.ModelAdmin):
    fields = [field.name for field in Match._meta.get_fields()]
    fields.remove("id")
    fields.remove("active_set")
    fields.remove("client_os")


class EndedMatchesAdmin(admin.ModelAdmin):
    fields = [field.name for field in Match._meta.get_fields()]
    fields.remove("id")
    fields.remove("active_set")


admin.site.register(Sports, SportsAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(EndedMatches, EndedMatchesAdmin)