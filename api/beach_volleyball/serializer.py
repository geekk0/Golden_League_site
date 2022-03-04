from django.contrib.auth.models import User, Group
from rest_framework import serializers
from sport_site.models import Match


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = [field.name for field in Match._meta.get_fields()]
        fields.remove("id")
        fields.remove("active_set")




