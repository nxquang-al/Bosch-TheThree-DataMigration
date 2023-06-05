import psutil
import os
import re


def check_file_is_running(filename):
    system = 'Linux'

    full_path = os.path.abspath(filename)

    if system:
        return file_running_in_Linux(full_path)
    elif system == 'Windows':
        return has_handle_in_Windows(full_path)


def iterate_fds(pid):
    dir = '/proc/'+str(pid)+'/fd'
    if not os.access(dir, os.R_OK | os.X_OK):
        return

    for fds in os.listdir(dir):
        for fd in fds:
            full_name = os.path.join(dir, fd)
            try:
                file = os.readlink(full_name)
                if file == '/dev/null' or \
                        re.match(r'pipe:\[\d+\]', file) or \
                        re.match(r'socket:\[\d+\]', file):
                    file = None
            except OSError as err:
                if err.errno == 2:
                    file = None
                else:
                    raise (err)

            yield (fd, file)


def has_handle_in_Windows(full_path):
    for proc in psutil.process_iter():
        try:
            for item in proc.open_files():
                if full_path == item.path:
                    return True
        except Exception:
            pass

    return False


def file_running_in_Linux(full_path):
    wildcard = "/proc/*/fd/*"
    lfds = glob.glob(wildcard)
    for fds in lfds:
        try:
            file = os.readlink(fds)
            if file == full_path:
                return True
        except OSError as err:
            if err.errno == 2:
                file = None
            else:
                raise (err)
    return False
