import datetime
import itertools
import ast
import json
import sys

import pdfcrowd
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .models import Sports, Match, EndedMatches
from django.views.generic import DetailView, View
from .forms import LoginForm, SquadForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa


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


def logout(request):
    user = logout(request)

    logout(user)


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

    if request.user.groups.filter(name='Referees').exists():
        user_is_referee = True
    else:
        user_is_referee = False

    if matches.exists():

        for match in matches:
            expire_time = datetime.timedelta(seconds=4)

            if match.ace_out_time is not None:
                if timezone.now() - match.ace_out_time > expire_time:
                    match.red_ace_out = " "
                    match.blue_ace_out = " "
                    match.ace_out_time = None

        match.save()

        context = {"matches": matches, "user_is_referee": user_is_referee}
        return render(request, "beach_volleyball.html", context)
    elif user_is_referee:
        return HttpResponseRedirect("/Регистрация команд/%s" % sport_name)
    else:
        return HttpResponseRedirect("/")


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


def change_points(request, match_id, team, action, ace_out=""):

    match = Match.objects.get(id=match_id)

    set = str(match.active_set)

    print(ace_out)

    if action == "plus":
        points = getattr(match, team+"_points_set_"+set)
        setattr(match, team+"_points_set_"+set, points + 1)

        match.current_inning = team

        list_inning_points = getattr(match, "inning_points_" + set).split(" ")

        if ace_out == "Ace":
            if team == "red":

                list_inning_points.append(str(getattr(match, "red_points_set_" + set))+"_Ace" + "--" +
                                          str(getattr(match, "blue_points_set_" + set)))
            if team == "blue":
                list_inning_points.append(str(getattr(match, "red_points_set_" + set)) + "--" +
                                          str(getattr(match, "blue_points_set_" + set)) + "_Ace")

        elif ace_out == "Out":
            if team == "red":
                list_inning_points.append(str(getattr(match, "red_points_set_" + set)) + "--" +
                                          str(getattr(match, "blue_points_set_" + set)) + "_Out")
            if team == "blue":
                list_inning_points.append(str(getattr(match, "red_points_set_" + set)) + "_Out" + "--" +
                                          str(getattr(match, "blue_points_set_" + set)))

        else:

            list_inning_points.append(str(getattr(match, "red_points_set_" + set)) +
                                      "--" + str(getattr(match, "blue_points_set_" + set)))

        print(list_inning_points)

        inning_points_str = " ".join(list_inning_points)

        print(inning_points_str)

        setattr(match, "inning_points_"+set, inning_points_str)


    else:
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


def set_inning(request, match_id, team):

    match = Match.objects.get(id=match_id)

    match.current_inning = team

    match.save()

    return HttpResponseRedirect("/Пляжный волейбол/Матч")


def swap_controls(request, match_id):

    match = Match.objects.get(id=match_id)

    if match.swap_position == 1:
        match.swap_position = 2
    else:
        match.swap_position = 1

    match.save()

    return HttpResponseRedirect("/Пляжный волейбол/Матч")


def ace_out(request, match_id, team, action):

    match = Match.objects.get(id=match_id)

    setattr(match, team + "_ace_out", action)

    match.ace_out_time = timezone.now()

    match.save()

    if action == "Ace":
        change_points(request, match_id=match_id, team=team, action="plus", ace_out="Ace")
        # return HttpResponseRedirect("/Изменить счет/"+str(match_id)+"/"+team+"/plus")

    if action == "Out":
        if team == "red":
            change_points(request, match_id=match_id, team="blue", action="plus", ace_out="Out")
        if team == "blue":
            change_points(request, match_id=match_id, team="red", action="plus", ace_out="Out")



    return HttpResponseRedirect("/Пляжный волейбол/Матч")


def end_set(request, match_id):

    match = Match.objects.get(id=match_id)
    set = str(match.active_set)

    if match.red_set_score > 2 or match.blue_set_score > 2:
        match.save()

    if getattr(match, "red_points_set_" + set) > getattr(match, "blue_points_set_" + set):
        match.red_set_score += 1
    elif getattr(match, "blue_points_set_" + set) > getattr(match, "red_points_set_" + set):
        match.blue_set_score += 1

    match.active_set += 1

    match.current_inning = "blank"

    match.save()



    return HttpResponseRedirect("/Пляжный волейбол/Матч")


def create_match(sport, red_team, blue_team):
    sport_type = Sports.objects.get(id=sport)
    match = Match.objects.create(sport=sport_type, red_squad=red_team.value(), blue_squad=blue_team.value())
    match.created_date = timezone.now()
    match.save()

    """statistic_file = open("Протокол по пляжному волейболу "+str(match.id)+".html", 'w', encoding="utf-8")
    statistic_file.close()"""

    return match


def end_match(request):
    match = Match.objects.all().first()

    ended_match = EndedMatches.objects.create(sport=match.sport, id=match.id, date=match.date, red_squad=match.red_squad,
                                              blue_squad=match.blue_squad)

    ended_match.red_set_score = match.red_set_score
    ended_match.blue_set_score = match.blue_set_score
    ended_match.red_points_set_1 = match.red_points_set_1
    ended_match.red_points_set_2 = match.red_points_set_2
    ended_match.red_points_set_3 = match.red_points_set_3
    ended_match.blue_points_set_1 = match.blue_points_set_1
    ended_match.blue_points_set_2 = match.blue_points_set_2
    ended_match.blue_points_set_3 = match.blue_points_set_3
    ended_match.inning_points_1 = match.inning_points_1
    ended_match.inning_points_2 = match.inning_points_2
    ended_match.inning_points_3 = match.inning_points_3




    ended_match.save()

    match.delete()

    return HttpResponseRedirect("/")


@login_required
def main(request):
    sports = Sports.objects.all()

    context = {"sports": sports}

    return render(request, "sports.html", context)


@login_required
def statistic_view(request, match_id):

    if Match.objects.filter(id=match_id).exists():

        match = Match.objects.filter(id=match_id).first()

    else:
        match = EndedMatches.objects.filter(id=match_id).first()

    """red_points_1 = get_points_lists(match_id, match.red_points_set_1)
    red_points_2 = get_points_lists(match_id, match.red_points_set_2)
    red_points_3 = get_points_lists(match_id, match.red_points_set_3)
    blue_points_1 = get_points_lists(match_id, match.blue_points_set_1)
    blue_points_2 = get_points_lists(match_id, match.blue_points_set_2)
    blue_points_3 = get_points_lists(match_id, match.blue_points_set_3)"""

    context = {"match": match}

    inning_points_1 = match.inning_points_1.split(" ")
    inning_points_2 = match.inning_points_2.split(" ")
    inning_points_3 = match.inning_points_3.split(" ")

    if inning_points_1:
        context["inning_points_1"] = inning_points_1
    if inning_points_2:
        context["inning_points_2"] = inning_points_2
    if inning_points_3:
        context["inning_points_3"] = inning_points_3

    """if red_points_1 and blue_points_1:
        set_1_points = itertools.zip_longest(red_points_1, blue_points_1, fillvalue="")
        context["set_1_points"] = set_1_points
    if red_points_2 and blue_points_2:
        set_2_points = itertools.zip_longest(red_points_2, blue_points_2, fillvalue="")
        context["set_2_points"] = set_2_points
    if red_points_3 and blue_points_3:
        set_3_points = itertools.zip_longest(red_points_3, blue_points_3, fillvalue="")
        context["set_3_points"] = set_3_points"""

    return render(request, "Протокол шаблон.html", context)


def get_points_lists(match_id, points):

    if Match.objects.filter(id=match_id).exists():

        match = Match.objects.filter(id=match_id).first()

    else:
        match = EndedMatches.objects.filter(id=match_id).first()

    points_list = []

    for i in range(1, points+1):
        if match.red_ace_out != " ":
            points_list.append(str(i) + " "+match.red_ace_out)
        else:
            points_list.append(i)

    return points_list




"""def html_to_pdf(request):
    try:
        # create the API client instance
        client = pdfcrowd.HtmlToPdfClient('demo', 'ce544b6ea52a5621fb9d55f8b542d14d')

        # run the conversion and write the result to a file
        client.convertUrlToFile("http://185.18.202.239/%D0%A1%D1%82%D0%B0%D1%82%D0%B8%D1%81%D1%82%D0%B8%D0%BA%D0%B0/36",
                                "test_static")
    except pdfcrowd.Error as why:
        # report the error
        sys.stderr.write('Pdfcrowd Error: {}\n'.format(why))

        # rethrow or handle the exception
        raise"""

"""path("get_pdf", views.html_to_pdf, name="get_pdf")"""
