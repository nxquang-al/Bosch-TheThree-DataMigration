import psutil
import os
import re
import argparse


def init_argument():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i", "--input_file", help="Directory to input file. Accepts file *.reqif or *.xml only")
    parser.add_argument("-o", "--output_file",
                        help="Directory to output *.json file.")

    args = parser.parse_args()

    INP_SRC, OUT_SRC = args.input_file, args.output_file
    CONFIG_SRC = 'config.yml'

    return INP_SRC, OUT_SRC, CONFIG_SRC


def find_keys(node, kv):
    """
    The function recursively searches for a specific key in a nested dictionary and returns its value.

    :param node: The node parameter is the current node being searched in the recursive function. It can
    be either a dictionary or a list
    :param kv: kv stands for "key value" and is a parameter that represents the key that we want to
    search for in a nested dictionary or list. The function "find_keys" recursively searches through the
    nested structure and yields the values associated with the specified key
    """
    if isinstance(node, list):
        for i in node:
            for x in find_keys(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in find_keys(j, kv):
                yield x


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
