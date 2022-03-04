from sport_site.models import Match
from rest_framework import viewsets
from rest_framework import permissions
from api.beach_volleyball.serializer import MatchSerializer


class GetMatchData(viewsets.ModelViewSet):
    def get_queryset(self):

        queryset = Match.objects.all()

        return queryset

    def get_serializer_class(self):
        serializer_class = MatchSerializer
        return serializer_class

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated()]
        return permission_classes


"""class Subscribe(viewsets.ModelViewSet):
    def get_queryset(self):
        user = self.request.user
        user_group = Group.objects.get(user=user)
        print(user, user_group)
        user_switch_date = Record.objects.filter(author_group=user_group).latest('report_date').report_date
        print(user_switch_date)
        print(type(user_switch_date))
        if user.has_perm('journal.change_record') or user_group.objects.filter(name="Трудовые резервы"):
            sub_type = '1'
        else:
            sub_type = '3'
        context = {'user_switch_date': user_switch_date, "sub_type": sub_type}
        return context

    def get_serializer_class(self):
        serializer_class = AuthSerializer
        return serializer_class"""
