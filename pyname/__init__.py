"""
docs


TODO
[ ] make it configurable
[ ] shorten values...
"""
import argparse
import sys
import pickle
from types import ModuleType
from pathlib import Path
import collections
from uuid import uuid4
import os

HIST_PATH = Path("~/.pyname/").expanduser()
HIST_PATH.mkdir(parents=True, exist_ok=True)
ARG_SEP = ","
LIMIT = 10
MAX_LEN = 100
UNIQUE_NEW_N = 5

FLAT_SEP = '.'


def flatten_obj(obj, parent_key="", sep=FLAT_SEP, squeeze=True) -> dict:
    """
    Flatten a nested dict.

    Args:
        obj: the dict waiting for flatting
        parent_key (str, optional): the parent key, will be a prefix in new key. Defaults to "".
        sep (str, optional): the separator for string connecting.

    Returns:
        dict: flatten dict
    """

    def get_new_key(parent_key, k):
        return parent_key + sep + str(k) if parent_key else k

    items = []
    if isinstance(obj, collections.abc.MutableMapping):
        items = list(obj.items())
    elif isinstance(obj, (list, tuple)) and any(not is_leaf_node(i) for i in obj):
        # For a list, if all element is basic, we prefer to not convert it to a dict
        items = [(i, v) for i, v in enumerate(obj)]
    else:
        return {parent_key: obj}

    res = []
    if len(items) == 1 and squeeze:
        res.extend(flatten_obj(items[0][1], parent_key, sep=sep).items())
    else:
        for k, v in items:
            res.extend(flatten_obj(v, get_new_key(parent_key, k), sep=sep).items())
    return dict(res)


def get_prev_obj_l(skip=0):
    files = sorted(HIST_PATH.glob("*"), key=os.path.getctime, reverse=True)
    res = []
    for i, fp in enumerate(files[skip:]):
        if i < LIMIT:
            with fp.open("rb") as f:
                res.append(pickle.load(f))
        else:
            fp.unlink()
    return res


def clear_prev_obj_l():
    for f in HIST_PATH.glob("*"):
        f.unlink()


def is_leaf_node(obj):
    return isinstance(obj, (str, int, float))

def convert_leaf_node(obj):
    if is_leaf_node(obj):
        return obj
    elif isinstance(obj, argparse.Namespace):
        # NOTE: assumption, all the info in argparse.Namespace are basic info
        return {"args": obj._get_args(), "kwargs": dict(obj._get_kwargs())}
    else:
        raise ValueError("Fail to converting leave node")


def convert2basic(obj):
    # try treat it as a leaf node first
    try:
        return convert_leaf_node(obj)
    except ValueError:
        pass

    # Not leaf node
    if isinstance(obj, list):
        return [convert2basic(i) for i in obj]
    elif isinstance(obj, tuple):
        return tuple(convert2basic(i) for i in obj)
    elif isinstance(obj, dict):
        return {convert2basic(k): convert2basic(v) for k, v in obj.items()}
    else:
        raise NotImplementedError(f"This type of input is not supported")


def get_short_name(obj: dict):
    """
    It is responsible for
    1) get a short name without conflicts (trying to be readable)
    2) converting the values to str
    """

    def _reverse(name):
        return ".".join(reversed(name.split(".")))

    def value2str(v):
        # 2) converting the values to str
        if isinstance(v, (list, tuple)):
            return ",".join(str(i) for i in v)
        else:
            return str(v)

    keys = list(obj)
    keys.sort(key=lambda k: (k.count(ARG_SEP), k.split()))
    new_dict = {}
    for k in keys:
        k_name = _reverse(k)
        for i in range(1, len(k_name) + 1):
            if k_name == ".":  # don't stop at separate
                continue
            prefix = k_name[:i]
            if prefix not in new_dict:
                new_dict[prefix] = value2str(obj[k])
                break
    return ",".join(f"{_reverse(k)}={v}" for k, v in new_dict.items())


class opt:
    # TODO: user can config sth in the __init__ function
    # TODO: get a batch of name
    def nameit(self, *args, **kwargs) -> str:
        """
        given any objects, give it an dirty name!!!!

        Returns
        -------
        str
            the name of objects
        """
        obj = convert2basic({"args": args, "kwargs": kwargs})
        with (HIST_PATH / str(uuid4())).open("wb") as f:
            pickle.dump(obj, f)

        obj = flatten_obj(obj)

        # if the name is short, just return it directly
        name = get_short_name(obj)
        if len(name) < MAX_LEN:
            return name

        # if the name is long. Then try to find its specialness
        skip = 1
        while True:  # try to find the special part
            prev_obj_l = get_prev_obj_l(skip=skip)  # skip the one we saved just now
            # only keep the important part of object

            prev_res = collections.defaultdict(set)
            for prev_obj in prev_obj_l:
                prev_obj = flatten_obj(prev_obj)
                for k, v in prev_obj.items():
                    prev_res[k].add(v)

            # FIXME: If long value is encountered, it may result in long name
            uniq_info = {}
            uniq_n_remain = UNIQUE_NEW_N
            for k, v in obj.items():
                if k not in prev_res and uniq_n_remain > 0:
                    uniq_n_remain -= 1
                    uniq_info[k] = v
                else:
                    # The new value is totally different from previous
                    if len(prev_res[k]) == 1 and next(iter(prev_res[k])) != v:
                        uniq_info[k] = v
            if len(uniq_info) > 0:
                return get_short_name(uniq_info)
            skip += 1


class CallableModule(ModuleType):
    """Make it callable"""

    def __call__(self, *args, **kwargs):
        return opt().nameit(*args, **kwargs)


sys.modules[__name__].__class__ = CallableModule