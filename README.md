## Golden League site                       
[switch to RUS](README.rus.md)

![python version](https://img.shields.io/badge/python-3.8.56-brightgreen)
![languages](https://img.shields.io/github/languages/top/geekk0/Golden_League_site)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/3cc6c94a88dd41be9b84faf38e378752)](https://www.codacy.com/gh/geekk0/Golden_League_site/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=geekk0/BRIO_assistant&amp;utm_campaign=Badge_Grade)
![last-commit](https://img.shields.io/github/last-commit/geekk0/Golden_League_site)

<br>Site for matches online streaming.

## Live demo
https://www.golden-league-stream.tk

##Description
<br>Service site section developed as part of live streaming system, which also contains [script](https://github.com/geekk0/Golden_League_captions) to form scoreboard (team, score) and telegram-bot for server condition and stream status tracking.
<br>Public site section displays matches schedule and results.
<br>During the match, referee use web-interface to form score and statistics. Script, the one running on OBS server, takes this data and creates text files, which are used on scene as scoreboard.
<br>Assembled stream is embedded to the corresponding site section.

## Features
 
- Referee interface, automated for beach volleyball rules, for maximum convenience and speed of use.
- Real time statistics system (players, team, H2H)
- Interface for viewing the score of the match with a minimum delay, for adjusting the odds of bets.
- Protocols of current and played matches
- Regular database backup script
- Script to remove obsolete .ts files generated by translation.
- Adapted for mobile devices.


## Using the referee interface

To start the match, you need to go to the Personal Account section, log in under the account login: referee, password: ref12345.<br>Select a sport, in case there is no active match, create teams from existing players or add new ones.
<br>To view the score of the match, log in under the account login: Spectator, password: spec12345.

## Libs

Django, Django REST Framework.
Request, Messages, ValueValidator, json, django.views.decorators.cache




