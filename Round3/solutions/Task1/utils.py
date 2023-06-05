import argparse
import os
import platform

import psutil


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


def is_locked(filename):
    system = platform.system()

    full_path = os.path.abspath(filename)

    if system == 'Linux':
        return is_locked_in_Linux(full_path)
    elif system == 'Windows':
        return is_locked_in_Windows(full_path)


def is_locked_in_Windows(full_path):
    for proc in psutil.process_iter():
        try:
            for item in proc.open_files():
                if full_path == item.path:
                    return True
        except Exception:
            print(full_path, '-> Failed to open file')

    return False


def is_file_locked(path):
    try:
        # Open the file in exclusive mode
        with open(path, 'r') as file:
            return False
    except IOError:
        # File is locked by another process
        return True


def is_directory_locked(path):
    try:
        # Attempt to rename the directory
        os.rename(path, path)
        return False
    except OSError:
        # Directory is locked by another process
        return True


def is_locked_in_Linux(path):
    if os.path.isfile(path):
        return is_file_locked(path)
    elif os.path.isdir(path):
        return is_directory_locked(path)
    else:
        print("The specified path does not exist.")
        return None
