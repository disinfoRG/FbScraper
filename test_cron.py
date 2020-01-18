from datetime import datetime

with open('test_cron.log', 'a') as f:
    f.write('\nAccessed on ' + str(datetime.now()))