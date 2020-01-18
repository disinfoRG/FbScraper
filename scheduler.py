from crontab import CronTab
from settings import USER, ROOT_FOLDER_PATH

cron = CronTab(user=USER)

for job in cron:
    print('-- removing a cron job: {}'.format(job))
    cron.remove(job)

job_test_cron = cron.new(command='source ~/.bashrc && cd {} && pipenv run python test_cron.py'.format(ROOT_FOLDER_PATH))
job_test_cron.minute.every(1)
job_discover = cron.new(command='source ~/.bashrc && cd {} && pipenv run python discover.py --all'.format(ROOT_FOLDER_PATH))
job_discover.hour.every(1)
job_update = cron.new(command='source ~/.bashrc && cd {} && pipenv run python update.py --all'.format(ROOT_FOLDER_PATH))
job_update.hour.every(1)

for job in cron:
    print('-- added a new cron job: {}'.format(job))

cron.write()


