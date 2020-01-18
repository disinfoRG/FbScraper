from crontab import CronTab

cron = CronTab(user='ta-shunlee')

job_discover = cron.new(command='cd /srv/web && pipenv run python discover.py --all')
job_discover.minute.every(5)
job_update = cron.new(command='cd /srv/web && pipenv run python update.py --all')
job_update.minute.every(5)

for item in cron:
    print(item)

cron.write()


