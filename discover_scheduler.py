import os
import re
from tqdm import tqdm

from helper import helper

def get_latest_created_logfile_path():
    logfiles = []
    logfile_selector = 'discover_pid\d+_timestamp\d+.log'

    for fname in os.listdir('.'):
        if re.match(logfile_selector, fname):
            logfiles.append(fname)
    
    timestamp_selector = 'discover_pid\d+_timestamp(\d+).log'
    latest_created_at = 0
    latest_created_logfile_path = None

    for logf in logfiles:
        t = int(re.findall(timestamp_selector, logf)[0])
        if t > latest_created_at:
            latest_created_at = t
            latest_created_logfile_path = logf

    return latest_created_logfile_path

def get_selected_logs(logfile_path, selector='crawler_timestamp'):
    logs = [line.rstrip('\n') for line in open(logfile_path) if selector in line]
    return logs

def get_timestamp(s):
    try:
        return int(re.findall('timestamp_(\d+)', s)[0])
    except:
        return 0

def get_latest_process_timestamp(logfile_path):
    latest_timestamp = 0

    for log in get_selected_logs(logfile_path):
        log_time = get_timestamp(log)
        if log_time > latest_timestamp:
            latest_timestamp = log_time

    if latest_timestamp is 0:
        return None

    return latest_timestamp

def is_main_process_hanging(logfile_path, selector='scheduler_timestamp', max_retry_times=2, timeout=60*60):
    logs = get_selected_logs(logfile_path, selector)
    logs_in_time = [log for log in logs if (helper.now() - get_timestamp(log)) < timeout]
    return len(logs_in_time) > 2

def is_main_process_working(timeout = 60 * 10):
    fpath = get_latest_created_logfile_path()

    if fpath is None:
        return False

    latest_timestamp = get_latest_process_timestamp(fpath)

    if latest_timestamp is not None:
        if (helper.now() - latest_timestamp) > timeout:
            return False
    else:
        checkpoint_text = 'main-process-hanging-checkpoint'
        if is_main_process_hanging(fpath, checkpoint_text):
            return False
        else:
            with open(fpath, 'a', buffering=1) as f:
                checkpoint_timestamp = 'scheduler_timestamp_{}: {}\n'.format(helper.now(), checkpoint_text)
                f.write(checkpoint_timestamp)

    return True

def reset(logfile_path):
    # - kill all processes of python3 discover.py --all
    kill_main_process_command = "\
        running_mid=$(ps aux | grep 'discover.py --all' | awk '{print $2}' ORS=' ') \
        && echo Main Process PID: $running_mid >> %s \
        && kill $running_mid 2>&1 | tee -a %s \
        && wait $running_mid \
    " % (logfile_path, logfile_path)
    # - kill all chrome window session 
    kill_session_command = "\
        running_sid=$(ps aux | grep 'Chrome' | awk '{print $2}' ORS=' ') \
        && echo Chrome Window Session PID: $running_sid >> %s \
        && kill $running_sid 2>&1 | tee -a %s \
        && wait $running_sid \
    " % (logfile_path, logfile_path)
    # - kill all webdriver
    kill_webdriver_command = "\
        running_wid=$(ps aux | grep 'chromedriver' | awk '{print $2}' ORS=' ') \
        && echo Webdriver PID: $running_wid >> %s \
        && kill $running_wid 2>&1 | tee -a %s \
        && wait $running_wid \
    " % (logfile_path, logfile_path)

    os.system(kill_main_process_command)
    os.system(kill_session_command)
    os.system(kill_webdriver_command)

def wait_for_process_on(logfile_path, wait_for_logfile_created=10):
    total = wait_for_logfile_created
    with tqdm(total=total, file=logfile_path) as pbar:
        pbar.set_description('------ Wait {} seconds for new main process to be on ------'.format(total))
        for i in range(total):
            helper.wait(1)
            pbar.update(1)

def main():
    mlog_path = 'discover_scheduler.log'
    with open(mlog_path, 'a', buffering=1) as mlog:
        # - start new discover.py process
        main_process_command = 'python3 discover.py --all &'

        if is_main_process_working() is not True:
            kill_text = '[{}] ------ Kill unused or hanging processes ------\n'.format(helper.now())
            mlog.write(kill_text)
            reset(mlog_path)
            helper.wait(5)
            new_process_text = '[{}] ------ Create new main process ------\n'.format(helper.now())
            mlog.write(new_process_text)
            os.system(main_process_command)
            wait_for_process_on(mlog)
        
        logfile_path = get_latest_created_logfile_path()
        success_text = '[{}] status: 200, command: "{}", logfile: {}\n'.format(helper.now(), main_process_command, logfile_path)
        mlog.write(success_text)
        print(success_text)

def test():
    logfile_path = 'dddd.log'
    s = "\
        running_mid=$(ps aux | grep 'Chrome' | awk '{print $2}' ORS=' ') \
        && echo Main Process PID: $running_mid >> %s \
    " % (logfile_path)
    os.system(s)
    print('hold')

if __name__ == '__main__':
    main()


