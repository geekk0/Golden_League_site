import json

from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .models import Sports, Match, EndedMatches
from django.views.generic import DetailView, View
from .forms import LoginForm, SquadForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone


class LoginView(View):

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {'form': form}
        return render(request, 'login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)

                return HttpResponseRedirect('/')

        return render(request, 'login.html', {'form': form})


class SquadRegister(View):

    def get(self, request, *args, **kwargs):
        form = SquadForm(request.POST or None)
        context = {"form": form}
        return render(request, "team_registration.html", context)

    def post(self, request, *args, **kwargs):
        form = SquadForm(request.POST or None)
        red_team = form["red_squad"]
        blue_team = form["blue_squad"]
        sport = 1
        create_match(sport, red_team, blue_team)
        return HttpResponseRedirect("/Пляжный волейбол/Матч")


def enter_match(request, sport_name):
    matches = Match.objects.filter(sport__name=sport_name)

    if matches.exists():
        match_score = send_match_score(matches)
        context = {"matches": matches, "match_score": json.dumps(match_score)}
        return render(request, "beach_volleyball.html", context)
    else:
        return HttpResponseRedirect("/Регистрация команд/%s" % sport_name)


def send_match_score(queryset):

    match = queryset.first()

    match_score = [match.red_points_set_1, match.red_points_set_2, match.red_points_set_3, match.blue_points_set_1,
                   match.blue_points_set_2, match.blue_points_set_3, match.red_set_score,
                   match.blue_set_score, match.active_set, match.current_inning]

    return match_score


def match_score_save(request, match_id):

    match = Match.objects.get(id=match_id)

    match.red_points_set_1 = request.GET.get("red_points_1")
    match.red_points_set_2 = request.GET.get("red_points_2")
    match.red_points_set_3 = request.GET.get("red_points_3")
    match.blue_points_set_1 = request.GET.get("blue_points_1")
    match.blue_points_set_2 = request.GET.get("blue_points_2")
    match.blue_points_set_3 = request.GET.get("blue_points_3")
    match.red_set_score = request.GET.get("red_set_score")
    match.blue_set_score = request.GET.get("blue_set_score")
    match.active_set = request.GET.get("active_set")
    match.current_inning = request.GET.get("current_inning")

    match.client_os = request.GET.get("client_os")

    match.save()

    if match.client_os == "MacOS":
        return HttpResponse(status=100)
    else:
        return HttpResponse(status=204)


def create_match(sport, red_team, blue_team):
    sport_type = Sports.objects.get(id=sport)
    match = Match.objects.create(sport=sport_type, red_squad=red_team.value(), blue_squad=blue_team.value())
    match.created_date = timezone.now()
    match.save()

    return match


def end_match(request):
    match = Match.objects.all().first()

    ended_match = EndedMatches.objects.create(sport=match.sport, date=match.date, red_squad=match.red_squad,
                                              blue_squad=match.blue_squad)

    ended_match.red_set_score = match.red_set_score
    ended_match.blue_set_score = match.blue_set_score
    ended_match.red_points_set_1 = match.red_points_set_1
    ended_match.red_points_set_2 = match.red_points_set_2
    ended_match.red_points_set_3 = match.red_points_set_3
    ended_match.blue_points_set_1 = match.blue_points_set_1
    ended_match.blue_points_set_2 = match.blue_points_set_2
    ended_match.blue_points_set_3 = match.blue_points_set_3

    ended_match.save()

    match.delete()

    return HttpResponseRedirect("/")


@login_required
def main(request):
    sports = Sports.objects.all()

    context = {"sports": sports}

    return render(request, "sports.html", context)






