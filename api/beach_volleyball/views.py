from sport_site.models import Match
from rest_framework import viewsets
from rest_framework import permissions
from api.beach_volleyball.serializer import MatchSerializer


class GetMatchData(viewsets.ModelViewSet):
    def get_queryset(self):

        queryset = Match.objects.filter(active="Активный")

        return queryset

    def get_serializer_class(self):
        serializer_class = MatchSerializer
        return serializer_class

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated()]
        return permission_classes


