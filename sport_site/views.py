import datetime
import json
import os

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .models import Sports, Match, MatchDay, ScheduledMatches, Team, Player
from django.views.generic import DetailView, View, ListView, TemplateView
from .forms import LoginForm, SquadForm, ScheduleForm, ScheduleFormSet, ScheduleFormSetHelper, TeamForm, AddPlayerForm,\
    H2HSelectForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control, never_cache
from django.utils import timezone
from django.conf import settings
from crispy_forms.layout import Submit, Layout, Field
from django.contrib import messages
from django.db.models import Avg, Count, Min, Sum


class LoginView(View):

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)

        ended_matches = Match.objects.filter(active="Завершенный").order_by("-date")

        for match in ended_matches:
            match.get_name()

        context = {'form': form, "ended_matches": ended_matches}

        return render(request, 'login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)

                return HttpResponseRedirect('/Личный кабинет')

        return render(request, 'login.html', {'form': form})


def user_logout(request):
    request.user.set_unusable_password()
    logout(request)

    return HttpResponseRedirect("/Личный кабинет")


class SquadRegister(View):
    def get(self, request, *args, **kwargs):
        players = Player.objects.all()
        form = SquadForm(request.GET or None, data_list=players)
        context = {"form": form}
        return render(request, "team_registration.html", context)

    def post(self, request, *args, **kwargs):
        form = SquadForm(request.POST or None)
        red_team_name = form["red_team_name"].value()
        blue_team_name = form["blue_team_name"].value()

        sport = 1

        red_team_player_one = form["red_team_player_one"].value()
        red_team_player_two = form["red_team_player_two"].value()
        blue_team_player_one = form["blue_team_player_one"].value()
        blue_team_player_two = form["blue_team_player_two"].value()

        wrong_players = self.wrong_player_fields(red_team_player_one, red_team_player_two, blue_team_player_one,
                                                 blue_team_player_two)
        if wrong_players is False:
            current_red_team = get_or_create_team(red_team_player_one, red_team_player_two)
            current_blue_team = get_or_create_team(blue_team_player_one, blue_team_player_two)
            create_match(sport, red_team_name, blue_team_name, current_red_team, current_blue_team)
            return HttpResponseRedirect("/Пляжный волейбол/Матч")
        else:
            for player in wrong_players:
                messages.error(request, "Игрока " + player + " нет в базе")
            return HttpResponseRedirect("/Регистрация")

    def wrong_player_fields(self, red_team_player_one, red_team_player_two, blue_team_player_one, blue_team_player_two):
        form_players = []
        error_form_players = []
        form_players.append(red_team_player_one)
        form_players.append(red_team_player_two)
        form_players.append(blue_team_player_one)
        form_players.append(blue_team_player_two)

        for player in form_players:

            if player not in list(Player.objects.all().values_list("name", flat=True)):
                error_form_players.append(player)
        if error_form_players:
            return error_form_players
        else:
            return False


def get_or_create_team(team_player_one, team_player_two):
    if Team.objects.filter(name=team_player_one + "/" + team_player_two).exists():
        team_object = Team.objects.get(name=team_player_one + "/" + team_player_two)
    elif Team.objects.filter(name=team_player_two + "/" + team_player_one).exists():
        team_object = Team.objects.get(name=team_player_two + "/" + team_player_one)
    else:
        team_object = Team.objects.create(name=team_player_one + "/" + team_player_two)

    assign_players(team_player_one, team_player_two, team_object)
    return team_object


def assign_players(first_player, second_player, team_object):
    first_player_object = Player.objects.get(name=first_player)
    first_player_object.number = 1
    second_player_object = Player.objects.get(name=second_player)
    second_player_object.number = 2

    first_player_object.team.add(team_object.id)
    first_player_object.save()
    second_player_object.team.add(team_object.id)
    second_player_object.save()


def create_match(sport, red_team_name, blue_team_name, red_team_object, blue_team_object):
    sport_type = Sports.objects.get(id=sport)
    match = Match.objects.create(sport=sport_type, red_squad=red_team_name, blue_squad=blue_team_name,
                                 date=timezone.now(), active="Активный")
    match.name = str(match.date.strftime("%d.%m.%y %H:%M ")) + red_team_object.name + " - " + blue_team_object.name \
            + " (" + str(match.id) + ")"
    match.red_team = red_team_object
    match.blue_team = blue_team_object

    match.save()

    match.__str__()

    return match


class AddPlayer(View):
    def get(self, request, *args, **kwargs):
        form = AddPlayerForm(request.GET or None)
        context = {"form": form}
        return render(request, "add_player.html", context)

    def post(self, request, *args, **kwargs):
        form = AddPlayerForm(request.POST or None)
        name = form["name"].value()
        create_player(name)
        return HttpResponseRedirect("/Регистрация")


def create_player(name):
    player_object = Player.objects.filter(name=name)
    if not player_object.exists():
        new_player_object = Player.objects.create(name=name)
        new_player_object.save()
        return HttpResponseRedirect("/Регистрация")

    else:
        messages.error(request=request, message="Игрок " + name + " уже присутствует в базе")
        return HttpResponseRedirect("/")


@login_required
def register_dp(request, sport_name):
    matches = Match.objects.filter(sport__name=sport_name, active="Активный")

    if matches.exists():
        return HttpResponseRedirect("/Личный кабинет")
    else:
        return HttpResponseRedirect("/Регистрация")


def enter_match(request, sport_name):
    matches = Match.objects.filter(sport__name=sport_name, active="Активный")

    if request.user.groups.filter(name='Referees').exists():
        user_is_referee = True
    else:
        user_is_referee = False

    device = check_user_device(request)

    if matches.exists():

        match = matches.first()

        red_team = Player.objects.filter(team=match.red_team)
        blue_team = Player.objects.filter(team=match.blue_team)

        expire_time = datetime.timedelta(seconds=4)

        if match.ace_out_time is not None:
            if timezone.now() - match.ace_out_time > expire_time:
                match.red_ace_out = " "
                match.blue_ace_out = " "
                match.ace_out_time = None

        match.save()

        left_inning = "not set"
        for player in Player.objects.filter(team=match.red_team):

            if not player.inning == "False":
                left_inning = "set"

        right_inning = "not set"
        for player in Player.objects.filter(team=match.blue_team):
            if not player.inning == "False":
                right_inning = "set"

        innings_set = [left_inning, right_inning]

        context = {"matches": matches, "user_is_referee": user_is_referee, "red_team": red_team, "blue_team": blue_team,
                   "innings_set": innings_set, "device": device}

        if request.user.is_staff:
            return render(request, "beach_volleyball.html", context)
        else:
            return HttpResponseRedirect("/Личный кабинет")
    elif user_is_referee:
        return HttpResponseRedirect("/Регистрация команд/%s" % sport_name)
    else:
        return HttpResponseRedirect("/Личный кабинет")


def check_ace_out(red_ace_out, blue_ace_out, ace_out_time):

    reset_ace_out_time = datetime.timedelta(seconds=5)

    if ace_out_time is None:
        red_ace_out_value = red_ace_out
        blue_ace_out_value = blue_ace_out
        ace_out_time_value = None

    elif red_ace_out != (" " or "undefined"):
        if timezone.now() - reset_ace_out_time > ace_out_time:
            ace_out_time_value = timezone.now()
            red_ace_out_value = " "
            blue_ace_out_value = " "
        else:
            red_ace_out_value = red_ace_out
            blue_ace_out_value = " "
            ace_out_time_value = None

    elif blue_ace_out != (" " or "undefined"):
        if timezone.now() - reset_ace_out_time > ace_out_time:
            ace_out_time_value = timezone.now()
            blue_ace_out_value = " "
            red_ace_out_value = " "
        else:
            red_ace_out_value = " "
            blue_ace_out_value = blue_ace_out
            ace_out_time_value = None

    return red_ace_out_value, blue_ace_out_value, ace_out_time_value


def change_points(request, match_id, team, action, player_id=33, ace_out=""):

    match = Match.objects.get(id=match_id)

    team_name = match.red_team.name

    set = str(match.active_set)

    if action == "plus":

        player_object = Player.objects.get(id=player_id)

        point_back_list = [team_name, action, str(player_id), ace_out]

        match.point_back_value = json.dumps(point_back_list, ensure_ascii=False)

        match.save()

        print(Player.objects.filter(inning="Active"))

        update_player_stat(player_object, action="plus_point", match_id=match_id)

        if check_scoring_team(player_object, match) and ace_out == "":
            rotation(match, player_object, action="scored")

            point_back_list = [team_name, action, str(player_id), ace_out, "rotation"]

            match.point_back_value = json.dumps(point_back_list, ensure_ascii=False)

            match.save()

        points = getattr(match, team+"_points_set_"+set)
        setattr(match, team+"_points_set_"+set, points + 1)

        match.current_inning = team

        list_inning_points = getattr(match, "inning_points_" + set).split(" ")

        if ace_out == "Ace":

            update_player_stat(player_object, action="ace", match_id=match_id)

            if team == "red":

                list_inning_points.append("(A)" + str(getattr(match, "red_points_set_" + set)) + "—" +
                                          str(getattr(match, "blue_points_set_" + set)))
            if team == "blue":
                list_inning_points.append(str(getattr(match, "red_points_set_" + set)) + "—" +
                                          str(getattr(match, "blue_points_set_" + set)) + "(A)")

        elif ace_out == "Out":
            rotation(match, player_object, action="out")
            update_player_stat(player_object, action="out", match_id=match_id)
            point_back_list = [team_name, action, str(player_id), ace_out, "rotation"]

            match.point_back_value = json.dumps(point_back_list, ensure_ascii=False)

            match.save()

            if team == "red":
                list_inning_points.append(str(getattr(match, "red_points_set_" + set)) + "—" +
                                          str(getattr(match, "blue_points_set_" + set)) + "(O)")
            if team == "blue":
                list_inning_points.append("(O)" + str(getattr(match, "red_points_set_" + set)) + "—" +
                                          str(getattr(match, "blue_points_set_" + set)))

        else:
            list_inning_points.append(str(getattr(match, "red_points_set_" + set)) +
                                      "—" + str(getattr(match, "blue_points_set_" + set)))

        inning_points_str = " ".join(list_inning_points)

        setattr(match, "inning_points_"+set, inning_points_str)

    else:

        player_object = Player.objects.get(id=json.loads(match.point_back_value)[2])

        update_player_stat(player_object, action="minus_point", match_id=match_id)

        if check_rotation_happened(match):
            recall_last_rotation(match)

        points = getattr(match, team + "_points_set_" + set)
        if points == 0:
            points = 0
        else:
            points -= 1
        setattr(match, team + "_points_set_" + set, points)

        list_inning_points = getattr(match, "inning_points_" + set).split(" ")[:-1]

        inning_points_str = " ".join(list_inning_points)

        setattr(match, "inning_points_" + set, inning_points_str)

    match.total_current_set = getattr(match, "red_points_set_"+set) + getattr(match, "blue_points_set_"+set)
    match.red_team_total = match.red_points_set_1 + match.red_points_set_2 + match.red_points_set_3
    match.blue_team_total = match.blue_points_set_1 + match.blue_points_set_2 + match.blue_points_set_3
    match.match_total = match.red_team_total + match.blue_team_total

    match.save()

    return HttpResponseRedirect("/Пляжный волейбол/Матч")


def check_user_device(request):
    user_agent = request.META['HTTP_USER_AGENT']
    if 'Mobile' in user_agent:
        device = "mobile"
    else:
        device = "desktop"
    print(device)
    return device


def check_rotation_happened(match):
    point_back = json.loads(match.point_back_value)

    if len(point_back) > 4:
        return True
    else:
        return False


def set_inning(request, match_id, team, player_name):

    match = Match.objects.get(id=match_id)

    match.current_inning = team

    match.save()

    player_object = Player.objects.get(name=player_name)

    player_object.inning = "Active"

    player_team_qs = player_object.team.filter(name=match.red_team)

    if player_team_qs.exists():
        player_team = player_team_qs.first()
        opposite_team = Team.objects.get(name=match.blue_team)
    else:
        player_team = player_object.team.get(name=match.blue_team)
        opposite_team = Team.objects.get(name=match.red_team)

    for player in Player.objects.filter(team=opposite_team):
        if player.inning == "Active":
            player.inning = "second"
        player.save()

    teammate = Player.objects.filter(team=player_team).exclude(id=player_object.id).first()

    teammate.inning = "first"

    player_object.save()
    teammate.save()

    return HttpResponseRedirect("/Пляжный волейбол/Матч")


def swap_controls(request, match_id):

    match = Match.objects.get(id=match_id)

    if match.swap_position == 1:
        match.swap_position = 2
    else:
        match.swap_position = 1

    match.save()

    return HttpResponseRedirect("/Пляжный волейбол/Матч")


def ace_out(request, match_id, action, player_id=20):

    match = Match.objects.get(id=match_id)

    if Player.objects.filter(team=match.red_team.id).filter(inning="Active").exists():
        team = "red"
    else:
        team = "blue"

    setattr(match, team + "_ace_out", action)

    match.ace_out_time = timezone.now()

    match.save()

    player = Player.objects.filter(team=match.red_team.id).filter(inning="Active") | \
        Player.objects.filter(team=match.blue_team.id).filter(inning="Active")

    if action == "Ace":

        change_points(request, match_id=match_id, team=team, action="plus", player_id=player.first().id, ace_out="Ace")

    if action == "Out":
        if team == "red":
            change_points(request, match_id=match_id, team="blue", action="plus", player_id=player.first().id,
                          ace_out="Out")
        if team == "blue":
            change_points(request, match_id=match_id, team="red", action="plus", player_id=player.first().id,
                          ace_out="Out")

    return HttpResponseRedirect("/Пляжный волейбол/Матч")


def end_set(request, match_id):

    match = Match.objects.get(id=match_id)
    set = str(match.active_set)

    for player in Player.objects.filter(team=match.red_team) | Player.objects.filter(team=match.blue_team):
        player.inning = "False"
        player.save()

    if match.red_set_score > 2 or match.blue_set_score > 2:
        match.save()

    if not getattr(match, "red_points_set_" + set) == getattr(match, "blue_points_set_" + set):
        if getattr(match, "red_points_set_" + set) > getattr(match, "blue_points_set_" + set):
            match.red_set_score += 1
            update_set_stat(match_id, "red")
        elif getattr(match, "blue_points_set_" + set) > getattr(match, "red_points_set_" + set):
            match.blue_set_score += 1
            update_set_stat(match_id, "blue")
        match.active_set += 1

        match.current_inning = "blank"

        match.save()

        return HttpResponseRedirect("/Пляжный волейбол/Матч")

    else:
        return HttpResponse(status=204)


def end_match(request):
    match = Match.objects.all().get(active="Активный")

    finalize_match_team_stats(match_id=match.id)
    finalize_match_player_stats(match_id=match.id)

    match.active = "Завершенный"

    match.save()

    return HttpResponseRedirect("/Личный кабинет")


def kill_match(request, match_id):
    match = Match.objects.get(id=match_id)

    red_team_object = match.red_team
    blue_team_object = match.blue_team

    for player in Player.objects.filter(team=red_team_object) | Player.objects.filter(team=blue_team_object):
        player_stats_rollback(player, match)

    if Match.objects.filter(red_team=red_team_object).count() == 1:
        red_team_object.delete()
    if Match.objects.filter(blue_team=blue_team_object).count() == 1:
        blue_team_object.delete()

    """else:
        team_stats_rollback(match, red_team_object, blue_team_object)"""

    match.delete()

    return HttpResponseRedirect("/Личный кабинет")


def player_stats_rollback(player, match):
    player.points_total_season -= player.current_match_points
    player.innings -= player.current_match_innings
    player.aces_total_season -= player.current_match_aces
    player.outs_total_season -= player.current_match_outs
    player.sets -= (match.active_set - 1)
    player_stats_zeroing(player)
    player.save()


def player_stats_zeroing(player):
    player.current_match_points = 0
    player.current_match_innings = 0
    player.current_match_aces = 0
    player.current_match_outs = 0
    player.inning = "False"
    player.save()


def team_stats_rollback(match, red_team, blue_team):
    red_team.sets_played -= match.active_set - 1
    red_team.sets_won -= match.red_set_score
    red_team.total_points -= match.red_team_total
    current_match_red_team_aces = sum(Player.objects.filter(team=red_team).values_list("current_match_aces", flat=True))
    red_team.aces -= current_match_red_team_aces
    current_match_red_team_outs = sum(Player.objects.filter(team=red_team).values_list("current_match_outs", flat=True))
    red_team.outs -= current_match_red_team_outs

    blue_team.sets_played -= match.active_set - 1
    blue_team.sets_won -= match.blue_set_score
    blue_team.total_points -= match.blue_team_total
    current_match_blue_team_aces = sum(Player.objects.filter(team=blue_team).values_list("current_match_aces",
                                                                                         flat=True))
    blue_team.aces -= current_match_blue_team_aces
    current_match_blue_team_outs = sum(Player.objects.filter(team=blue_team).values_list("current_match_outs",
                                                                                         flat=True))
    blue_team.outs -= current_match_blue_team_outs

    red_team.save()
    blue_team.save()


@login_required
def main(request):
    sports = Sports.objects.all()

    context = {"sports": sports}

    return render(request, "sports.html", context)


def statistic_view(request, match_id, pdf=None):

    if request.user.is_staff:
        staff = True
    else:
        staff = False

    context = {"staff": staff}

    if Match.objects.filter(id=match_id).exists():

        match = Match.objects.get(id=match_id)

        context["match"] = match

        if match.inning_points_1:
            inning_points_1 = match.inning_points_1.split(" ")
            context["inning_points_1"] = inning_points_1[1:]
        if match.inning_points_2:
            inning_points_2 = match.inning_points_2.split(" ")
            context["inning_points_2"] = inning_points_2[1:]
        if match.inning_points_3:
            inning_points_3 = match.inning_points_3.split(" ")
            context["inning_points_3"] = inning_points_3[1:]

    if pdf:
        return context
    else:
        return render(request, "Протокол шаблон.html", context)


def show_stream(request):

    return render(request, "stream.html")


def detect_user_agent(request, stream_name):
    user_agent = request.META['HTTP_USER_AGENT']

    if "VLC" in user_agent:
        raise PermissionDenied()

    else:
        response = HttpResponse()
        response['X-Accel-Redirect'] = '/stream/hdn_url/' + stream_name
        return response


def get_rtmp_stream(request, stream_name):
    user_agent = request.META['HTTP_USER_AGENT']

    if "VLC" in user_agent:
        raise PermissionDenied()

    else:
        response = HttpResponse()
        response['X-Accel-Redirect'] = '/stream/rtmp/' + stream_name
        return response


def landing_page(request):

    context = {}

    if Match.objects.filter(active="Завершенный").exists():
        last_matches = Match.objects.filter(active="Завершенный").order_by("-date")[:7]

        archived_matches = Match.objects.filter(active="Завершенный").order_by("-date")[7:]

        context["archived_matches"] = archived_matches
        context["last_matches"] = last_matches

    if MatchDay.objects.all().exists():
        for day in MatchDay.objects.all():
            if day.day < datetime.date.today():
                day.delete()

        earliest_match_day = MatchDay.objects.all().order_by("day").earliest("day").day

        schedule_days = MatchDay.objects.filter(day__lte=earliest_match_day + datetime.timedelta(days=5))\
            .order_by("day")

        latest_match_day = schedule_days.latest("day").day

        context["schedule_days"] = schedule_days
        context["earliest_match_day"] = earliest_match_day
        context["latest_match_day"] = latest_match_day

    return render(request, "page26283709body.html", context)


def schedule_list(request):
    scheduled_days = MatchDay.objects.all().order_by('day')

    for day in scheduled_days:
        if day.day < datetime.date.today():
            day.delete()

    context = {"scheduled_days": scheduled_days}

    if request.user.username == "admin" or "Referee":

        return render(request, "schedule.html", context)

    else:

        return HttpResponseRedirect("")


class AddScheduledMatch(View):

    def get(self, *args, **kwargs):
        form = ScheduleForm(request.POST or None)
        context = {"form": form}
        return render(request, "schedule_match.html", context)

    def post(self, *args, **kwargs):
        form = ScheduleForm(request.POST or None)
        day = form["date"]
        time = form["time"]
        red_team = form["red_team"]
        blue_team = form["blue_team"]
        schedule_day_and_match(day.value(), time.value(), red_team.value(), blue_team.value())
        return HttpResponseRedirect("/Расписание")


class ScheduledMatchesView(ListView):
    model = ScheduledMatches
    template_name = "schedule.html"


class ScheduleMatchAddView(TemplateView):
    template_name = "schedule_match.html"

    def get(self, *args, **kwargs):
        formset = ScheduleFormSet(queryset=ScheduledMatches.objects.none())
        helper = ScheduleFormSetHelper()

        helper.form_method = 'POST'
        helper.add_input(Submit('submit', 'Сохранить', css_class='btn btn-success'))

        return self.render_to_response({"formset": formset, "helper": helper})

    def post(self, *args, **kwargs):

        formset = ScheduleFormSet(data=self.request.POST)
        helper = ScheduleFormSetHelper()

        helper.form_method = 'POST'

        for form in formset:

            try:
                day = form["date"].value()
                time = form["time"].value()
                red_team = form["red_team"].value()
                blue_team = form["blue_team"].value()
                schedule_day_and_match(day, time, red_team, blue_team)
            except:
                HttpResponseRedirect("/Добавить матч в расписание")

        return HttpResponseRedirect("/Расписание")


def schedule_day_and_match(day, time, red_team, blue_team):
    if MatchDay.objects.filter(day=day).count() < 1:
        new_match_day = MatchDay.objects.create(day=day)
        new_match_day.save()
    new_scheduled_match = ScheduledMatches.objects.create()
    new_scheduled_match.day = MatchDay.objects.get(day=day)
    new_scheduled_match.time = time
    new_scheduled_match.red_team = red_team
    new_scheduled_match.blue_team = blue_team
    new_scheduled_match.save()


def delete_matchday(request, matchday_id):
    matchday = MatchDay.objects.filter(id=matchday_id)
    matchday.delete()

    return HttpResponseRedirect("/Расписание")


def finalize_match_team_stats(match_id):
    match_object = Match.objects.get(id=match_id)
    red_team_object = Team.objects.get(id=match_object.red_team.id)
    blue_team_object = Team.objects.get(id=match_object.blue_team.id)
    if match_object.red_set_score > match_object.blue_set_score:
        red_team_object.games_won += 1
        if match_object.blue_set_score == 0:
            red_team_object.dry_wins += 1
    else:
        blue_team_object.games_won += 1
        if match_object.red_set_score == 0:
            blue_team_object.dry_wins += 1
    red_team_object.games_played += 1
    blue_team_object.games_played += 1

    red_team_object.get_win_percentage()
    blue_team_object.get_win_percentage()

    red_players = Player.objects.filter(team=red_team_object)
    blue_players = Player.objects.filter(team=blue_team_object)

    red_team_object.sets_won = match_object.red_set_score
    blue_team_object.sets_won = match_object.blue_set_score
    red_team_object.aces += sum(item.current_match_aces for item in red_players)
    blue_team_object.aces += sum(item.current_match_aces for item in blue_players)
    red_team_object.outs += sum(item.current_match_outs for item in red_players)
    blue_team_object.outs += sum(item.current_match_outs for item in blue_players)
    red_team_object.total_points += sum(item.current_match_points for item in red_players)
    blue_team_object.total_points += sum(item.current_match_points for item in blue_players)

    red_team_object.save()
    blue_team_object.save()


def finalize_match_player_stats(match_id):
    match_object = Match.objects.get(id=match_id)
    red_team_object = Team.objects.get(id=match_object.red_team.id)
    blue_team_object = Team.objects.get(id=match_object.blue_team.id)

    for player in Player.objects.filter(team=red_team_object) | Player.objects.filter(team=blue_team_object):

        if (match_object.red_set_score > match_object.blue_set_score and
            player.team.values_list("id", flat=True).first() is red_team_object.id) or \
                (match_object.blue_set_score > match_object.red_set_score and
                 player.team.values_list("id", flat=True).first() is blue_team_object):
            player.games_won += 1

        player.games += 1
        player.current_match_points = 0
        player.current_match_innings = 0
        player.current_match_aces = 0
        player.current_match_outs = 0
        player.save()


def update_set_stat(match_id, team):
    match_object = Match.objects.get(id=match_id)
    red_team_object = Team.objects.get(id=match_object.red_team.id)
    blue_team_object = Team.objects.get(id=match_object.blue_team.id)

    for player in Player.objects.filter(team=red_team_object) | Player.objects.filter(team=blue_team_object):
        update_player_stat(player, "plus_set", match_id=match_id)


def update_player_stat(player, action, match_id=300):
    player.get_best_teammate()
    player.get_worst_teammate()
    if action is "plus_point":
        player.points_total_season += 1
        player.current_match_points += 1
        print(Player.objects.filter(inning="Active"))
        inning_player_id = Player.objects.filter(inning="Active").first().id
        inning_player = Player.objects.get(id=inning_player_id)
        if player != inning_player:
            inning_player.innings += 1
            inning_player.current_match_innings += 1
            inning_player.save()
        else:
            player.innings += 1
            player.current_match_innings += 1
    elif action is "minus_point":
        match = Match.objects.get(id=match_id)
        if "Ace" in json.loads(match.point_back_value):
            player.current_match_aces -= 1
            player.aces_total_season -= 1
            if player.innings and player.current_match_innings > 0:
                player.innings -= 1
                player.current_match_innings -= 1
        player.points_total_season -= 1
        player.current_match_points -= 1
    elif action is "ace":
        player.aces_total_season += 1
        player.current_match_aces += 1

    elif action is "out":
        if player.current_match_points > 0:
            player.current_match_points -= 1
            player.points_total_season -= 1
        player.outs_total_season += 1
        player.current_match_outs += 1

    elif action is "plus_set":
        player.sets += 1
    player.save()


def stats_h2h(request, left_team_id=None, right_team_id=None):
    teams = Team.objects.all().order_by("name")
    players = Player.objects.all().order_by("name")
    matches = Match.objects.all().order_by("-date").filter(active="Завершенный")
    left_team_object = Team.objects.get(id=left_team_id)
    right_team_object = Team.objects.get(id=right_team_id)
    left_team_matches = Match.objects.filter(red_team=left_team_object).order_by("-date").filter(active="Завершенный") | Match.objects.filter(blue_team=left_team_object).order_by("-date").filter(active="Завершенный")
    right_team_matches = Match.objects.filter(red_team=right_team_object).order_by("-date").filter(active="Завершенный") | Match.objects.\
        filter(blue_team=right_team_object).order_by("-date").filter(active="Завершенный")
    rival_matches = Match.objects.filter(red_team=left_team_object).filter(blue_team=right_team_object).order_by("-date").filter(active="Завершенный") | Match.objects.\
        filter(red_team=right_team_object).filter(blue_team=left_team_object).order_by("-date").filter(active="Завершенный")
    if left_team_matches.exists() or right_team_matches.exists():
        selected = "True"
        active_teams = [str(left_team_id), str(right_team_id)]
    else:
        selected = "False"
        active_teams = None

    context = {"teams": teams, "players": players, "matches": matches, "left_team_matches": left_team_matches,
               "right_team_matches": right_team_matches, "selected": selected, "active_teams": active_teams,
               "rival_matches": rival_matches}
    return render(request, "statistics_H2H.html", context)


def rotation(match_object, player_object, action):

    save_last_rotation(match_object)

    player_team_qs = player_object.team.filter(name=match_object.red_team)

    if player_team_qs.exists():
        player_team = player_team_qs.first()
        opposite_team = Team.objects.get(name=match_object.blue_team)
    else:
        player_team = player_object.team.get(name=match_object.blue_team)
        opposite_team = Team.objects.get(name=match_object.red_team)

    if action == "scored":

        teammate = Player.objects.filter(team=player_team).exclude(id=player_object.id).first()

        if player_object.inning == "first":
            player_object.inning = "Active"
            teammate.inning = "first"
        elif player_object.inning == "second":
            player_object.inning = "first"
            teammate.inning = "Active"

        player_object.save()
        teammate.save()

        active_player_opp_id = Player.objects.filter(team=opposite_team.id).filter(inning="Active")
        if active_player_opp_id.exists():
            active_player = Player.objects.get(id=active_player_opp_id[0].id)
            active_player.inning = "second"
            active_player.save()

    if action == "out":

        teammate = Player.objects.filter(team=player_team).exclude(id=player_object.id).first()

        if player_object.inning == "Active":
            player_object.inning = "second"
            teammate.inning = "first"

            player_object.save()
            teammate.save()

            for player in Player.objects.filter(team=opposite_team):
                if player.inning == "first":
                    player.inning = "Active"
                elif player.inning == "second":
                    player.inning = "first"

                player.save()

        elif teammate.inning == "Active":
            teammate.inning = "second"
            player_object.inning = "first"

            player_object.save()
            teammate.save()

            for player in Player.objects.filter(team=opposite_team):
                if player.inning == "first":
                    player.inning = "Active"
                elif player.inning == "second":
                    player.inning = "first"

                player.save()


def check_scoring_team(player, match):
    player_team_qs = player.team.filter(name=match.red_team)

    if player_team_qs.exists():
        player_team = player_team_qs.first()
    else:
        player_team = player.team.get(name=match.blue_team)

    active_inning_player_same_team = Player.objects.filter(team=player_team).filter(inning="Active")

    if not active_inning_player_same_team.exists():
        return True
    else:
        return False


def save_last_rotation(match):

    inning_list = []

    for red_player in Player.objects.filter(team=match.red_team).order_by("number"):
        inning_list.append(red_player.inning)
    for blue_player in Player.objects.filter(team=match.blue_team).order_by("number"):
        inning_list.append(blue_player.inning)
    match.last_inning = json.dumps(inning_list)
    match.save()


def recall_last_rotation(match):

    inning_list = json.loads(match.last_inning)

    red_team_first_player = Player.objects.filter(team=match.red_team).filter(number=1).first()
    red_team_first_player.inning = inning_list[0]
    red_team_first_player.save()

    red_team_second_player = Player.objects.filter(team=match.red_team).filter(number=2).first()
    red_team_second_player.inning = inning_list[1]

    red_team_second_player.save()

    blue_team_first_player = Player.objects.filter(team=match.blue_team).filter(number=1).first()
    blue_team_first_player.inning = inning_list[2]

    blue_team_first_player.save()

    blue_team_second_player = Player.objects.filter(team=match.blue_team).filter(number=2).first()
    blue_team_second_player.inning = inning_list[3]

    blue_team_second_player.save()


@login_required
def stats_players(request):
    players = Player.objects.all()
    device = check_user_device(request)

    context = {"players": players, "device": device}

    return render(request, "statistcs_players.html", context)


@login_required
def stats_teams(request):
    teams = Team.objects.all()
    device = check_user_device(request)
    context = {"teams": teams, "device": device}

    return render(request, "statistics_teams.html", context)


class H2HSelectView(View):
    def get(self, request, *args, **kwargs):
        teams = Team.objects.all()
        form = H2HSelectForm(request.GET or None, data_list=teams)
        context = {"form": form}
        return render(request, "statistics_H2H.html", context)

    def post(self, request, *args, **kwargs):
        form = H2HSelectForm(request.POST or None)

        left_team = form["left_team"].value()
        right_team = form["right_team"].value()

        left_team_id = Team.objects.get(name=left_team).id
        right_team_id = Team.objects.get(name=right_team).id

        return HttpResponseRedirect("Статистика H2H/" + str(left_team_id) + "/" + str(right_team_id))






