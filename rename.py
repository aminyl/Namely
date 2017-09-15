""" Rename file name with its created time."""

import sys
import os
import datetime
import json
import collections

def _get_ext(path):
    _, ext = os.path.splitext(path)
    return ext

def _simple_ext(path):
    return _remove_dot(_get_ext(path)).lower()

def _remove_dot(ext):
    return ext[1:]

def _split_join(s, t):
    return t.join([s[:2], s[2:4], s[4:6]])

def _get_targets(target_ext):
    files = []
    for path in os.listdir("./"):
        ext = _simple_ext(path)
        if ext in target_ext:
            files.append(path)
    return files

def _get_name_correspondence(files):
    name_correspondence = {}
    for path in files:
        ext = _simple_ext(path)
        if ext in FROM_FILE_NAME_EXT:
            file_name = "20" + _split_join(path[:6], "-") + " " + _split_join(path[7:13], ".")
        else:
            time_stamp = datetime.datetime.fromtimestamp(os.stat(path).st_mtime)
            file_name = time_stamp.strftime("%Y-%m-%d %H.%M.%S")
        file_name += "." + ext
        name_correspondence[path] = file_name
    return name_correspondence

def _get_dup_name(name):
    dup = collections.Counter(name)
    for k, v in dup.items():
        if v == 1:
            del dup[k]
    return dup

def _prevent_duplication(name_correspondence):
    dup = _get_dup_name(name_correspondence.values())
    n = sum(dup.values()) - len(dup)
    i = 0
    for _ in range(n):
        dk, dv = dup.items()[0]
        for k, v in reversed(sorted(name_correspondence.items())):
            if v == dk:
                s = "_" * (dv - 1)
                ext = _get_ext(v)
                name_correspondence[k] = v.replace(ext, s + ext)
                dup[dk] -= 1
                if dup[dk] == 1:
                    del dup[dk]
                i += 1
                break

def _save_log(data):
    log_name = "log_" + datetime.datetime.now().strftime("%Y.%m%d.%H%M%S") + ".json"
    with open(log_name, 'w') as f:
        json.dump(data, f)

def _ren(names):
    for k, v in names.items():
        os.rename(k, v)

def _swap_key_value(d):
    return {v:k for k, v in d.items()}

def rename():
    files = _get_targets(PICTURE_EXT + MOVIE_EXT)
    name_correspondence = _get_name_correspondence(files)
    _prevent_duplication(name_correspondence)
    _save_log(name_correspondence)
    _ren(name_correspondence)

def restore(log_path):
    with open(log_path, 'r') as f:
        log = json.load(f)
    _ren(_swap_key_value(log))

def restore_latest():
    log_files = _get_targets(["json"])
    log_file = log_files[-1]
    restore(log_file)

PICTURE_EXT = ["jpg", "png"]
MOVIE_EXT = ["3gp"]
FROM_FILE_NAME_EXT = ["3gp"]

args = sys.argv
if len(args) == 1:
    rename()
elif len(args) == 2:
    restore(args[1])
