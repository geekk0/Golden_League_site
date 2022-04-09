import datetime
import itertools
import ast
import json
import sys
import os

import pdfcrowd
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .models import Sports, Match, EndedMatches, MatchDay, ScheduledMatches
from django.views.generic import DetailView, View
from .forms import LoginForm, SquadForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings



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
    matches = Match.objects.filter(sport__name=sport_name, active="Активный")

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

                list_inning_points.append("(A)" + str(getattr(match, "red_points_set_" + set)) + "—" +
                                          str(getattr(match, "blue_points_set_" + set)))
            if team == "blue":
                list_inning_points.append(str(getattr(match, "red_points_set_" + set)) + "—" +
                                          str(getattr(match, "blue_points_set_" + set)) + "(A)")

        elif ace_out == "Out":
            if team == "red":
                list_inning_points.append(str(getattr(match, "red_points_set_" + set)) + "—" +
                                          str(getattr(match, "blue_points_set_" + set)) + "(O)")
            if team == "blue":
                list_inning_points.append("(O)" + str(getattr(match, "red_points_set_" + set)) + "—" +
                                          str(getattr(match, "blue_points_set_" + set)))

        else:

            list_inning_points.append(str(getattr(match, "red_points_set_" + set)) +
                                      "—" + str(getattr(match, "blue_points_set_" + set)))

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
    match = Match.objects.create(sport=sport_type, red_squad=red_team.value(), blue_squad=blue_team.value(),
                                 date=timezone.now(), active="Активный")
    match.get_name()
    print(timezone.now())
    match.save()
    match.__str__()



    """statistic_file = open("Протокол по пляжному волейболу "+str(match.id)+".html", 'w', encoding="utf-8")
    statistic_file.close()"""

    return match


def end_match(request):
    match = Match.objects.all().get(active="Активный")

    match.active = "Завершенный"

    match.save()

    return HttpResponseRedirect("/Личный кабинет")


def kill_match(request, match_id):
    match = Match.objects.get(id=match_id)

    match.delete()

    return HttpResponseRedirect("/Личный кабинет")


"""def ended_to_match(request):

    for ended_match in EndedMatches.objects.all():

        match = Match.objects.create(id=ended_match.id, sport=ended_match.sport, date=ended_match.date, name=ended_match.name,
                                     red_squad=ended_match.red_squad, blue_squad=ended_match.blue_squad)

        match.red_set_score = ended_match.red_set_score
        match.blue_set_score = ended_match.blue_set_score
        match.red_points_set_1 = ended_match.red_points_set_1
        match.red_points_set_2 = ended_match.red_points_set_2
        match.red_points_set_3 = ended_match.red_points_set_3
        match.blue_points_set_1 = ended_match.blue_points_set_1
        match.blue_points_set_2 = ended_match.blue_points_set_2
        match.blue_points_set_3 = ended_match.blue_points_set_3
        match.inning_points_1 = ended_match.inning_points_1
        match.inning_points_2 = ended_match.inning_points_2
        match.inning_points_3 = ended_match.inning_points_3
        match.name = ended_match.name
        match.sport = ended_match.sport
        match.date = ended_match.date
        match.red_squad = ended_match.red_squad
        match.blue_squad = ended_match.blue_squad
        match.active_set = ended_match.active_set
        match.total_current_set = ended_match.total_current_set
        match.red_team_total = ended_match.red_team_total
        match.blue_team_total = ended_match.blue_team_total
        match.match_total = ended_match.match_total
        match.active = "Завершенный"

        match.save()

    return HttpResponse(status=204) """

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




"""def html_to_pdf(template_src, context_dict={}):

    pdfmetrics.registerFont(TTFont('Arial', "arialmt.ttf"))
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    p = canvas.Canvas(result)
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result, encoding='utf-8', show_error_as_pdf=True,
                            link_callback=fetch_pdf_resources)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        # getting the template
        # statistic_view(request, match_id=match_id)

        pdf = html_to_pdf('test.html')

        # rendering the template
        return HttpResponse(pdf, content_type='application/pdf')"""

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
                print("old")
                day.delete()

        earliest_match_day = MatchDay.objects.all().order_by("day").earliest("day").day

        schedule_days = MatchDay.objects.filter(day__lte=earliest_match_day + datetime.timedelta(days=5))\
            .order_by("day")

        latest_match_day = schedule_days.latest("day").day

        context["schedule_days"] = schedule_days
        context["earliest_match_day"] = earliest_match_day
        context["latest_match_day"] = latest_match_day

    return render(request, "page26283709body.html", context)





