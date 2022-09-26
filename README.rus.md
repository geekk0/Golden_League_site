## Golden League site                       
[переключить на ENG](README.md)

![python version](https://img.shields.io/badge/python-3.8.56-brightgreen)
![languages](https://img.shields.io/github/languages/top/geekk0/Golden_League_site)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/3cc6c94a88dd41be9b84faf38e378752)](https://www.codacy.com/gh/geekk0/Golden_League_site/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=geekk0/BRIO_assistant&amp;utm_campaign=Badge_Grade)
![last-commit](https://img.shields.io/github/last-commit/geekk0/Golden_League_site)

<br>Сайт для онлайн трансляций матчей.

## Live demo
https://www.golden-league-stream.tk

##Описание
<br>Закрытый раздел сайта разрабатывался как часть системы для организации трансляций, в которую также входят [скрипт](https://github.com/geekk0/Golden_League_captions) для формирования табло (команды, счет) и telegram-бот для отслеживания состояния сервера и статуса трансляции.
<br>На общедоступной части сайта отображается расписание предстоящих матчей и результаты сыгранных.
<br>В течение матча судья использует веб-интерфейс для формирования счета и статистики. Скрипт, запущенный на сервере OBS, берет эти данные и создает файлы, которые используются в сцене в качестве табло.
<br>Собранный поток трансляции встраивается в соответствующий раздел сайта.

## Особенности
 
- Интерфейс судьи, автоматизированный для правил пляжного волейбольного матча, для максимального удобства и скорости использования.
- Система формирующая статистику в реальном времени (игроки, команды, H2H)
- Интерфейс просмотра счета матча с минимальной задержкой, для регулирования коэффициентов ставок.
- Протоколы текущих и сыгранных матчей
- Скрипт регулярного резервирования базы данных
- Скрипт для удаления устаревших .ts файлов, создаваемых трансляцией.
- Адаптирован для мобильных устройств.

## Использование судейского интерфейса

Для начала матча необходимо перейти в раздел ЛК(Личный кабинет), залогиниться под учетной записью login: referee, password: ref12345.
<br>Выбрать вид спорта, в случае, если нет активного матча, создать команды из имеющихся игроков или добавить новых.
<br>Для просмотра счета матча залогиниться под учетной записью login: Spectator, password: spec12345.


## Библиотеки

Django, Django REST Framework.
Request, Messages, ValueValidator, json, django.views.decorators.cache
