import os
import time
import datetime
import schedule

cmd_dump = "python manage.py dumpdata > db_backup/dump_"
cmd_suffix = ".json"


def dump_db_file():
    print(datetime.date.today())
    cmd_date = datetime.date.today().strftime("%d%m")
    os.system(cmd_dump + cmd_date + cmd_suffix)

    return


schedule.every().day.at("19:00").do(dump_db_file)

while True:
    schedule.run_pending()
    time.sleep(1)
