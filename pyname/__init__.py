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
from typing import Callable
from uuid import uuid4
import logging
import os

HIST_PATH = Path("~/.pyname/").expanduser()
HIST_PATH.mkdir(parents=True, exist_ok=True)
ARG_SEP = ","
LIMIT = 10
MAX_LEN = 100
MAX_KEY_SIZE = 10  # the max number of keys to show in the name when the name is long and we only want to show MAX_KEY_SIZE unique key for the name
MAX_VALUE_LEN = 20  # the max length for the value when naming
NOT_APPEAR = "__NOT_APPEAR"  # if the key not appear in the previous object, then fill it with this value

FLAT_SEP = '.'
__version__ = '0.0.1.dev'


def flatten_obj(obj, parent_key="", sep=FLAT_SEP, squeeze=True) -> dict:
    """
    Flatten a nested dict.

    Args:
        obj: the dict waiting for flatting; It has been converted to basic object by convert2basic.
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
    elif is_leaf_node(obj) or isinstance(obj, (list, tuple)) and all(is_leaf_node(i) for i in obj) and len(obj) > 1:
        # For long basic object, we return the list directly
        return {parent_key: obj}
    elif isinstance(obj, (list, tuple)):
        # If there any node is not leaf node, we continue to expand it recursively
        items = [(i, v) for i, v in enumerate(obj)]
    else:
        raise NotImplementedError(f"This type of input is not supported; Please use `convert2basic` to convert it to basic type first")

    res = []
    if len(items) == 1 and squeeze and isinstance(obj, (list, tuple)):
        # NOTE:
        # only data like {"good": ["haha"]}  will be squeezed (return {"good": "haha"} instead of {"good.0": "haha"})
        # {"good":  {"xixi": "hah"}} will not be squeezed.  We think the inner most key represents the most uniqueness
        res.extend(flatten_obj(items[0][1], parent_key, sep=sep).items())
    else:
        for k, v in items:
            res.extend(flatten_obj(v, get_new_key(parent_key, k), sep=sep).items())
    return dict(res)


def is_leaf_node(obj):
    return isinstance(obj, (str, int, float, bool)) or obj is None


def convert_leaf_node(obj):
    if is_leaf_node(obj):
        return obj
    else:
        raise ValueError("Fail to converting leave node")


def convert2basic(obj):
    # try treat it as a leaf node first
    try:
        return convert_leaf_node(obj)
    except ValueError:
        pass

    # Not leaf node
    if isinstance(obj, (list, tuple)):
        # Because we want to make it hashable.
        # So list will be converted to tuple
        return tuple(convert2basic(i) for i in obj)
    elif isinstance(obj, dict):
        return {convert2basic(k): convert2basic(v) for k, v in obj.items()}
    elif isinstance(obj, argparse.Namespace):
        return {"args": convert2basic(obj._get_args()), "kwargs": convert2basic(dict(obj._get_kwargs()))}
    else:
        logging.info(f"{obj} with type {type(obj)} can't be handled. So it is converted to string")
        return str(obj)


def get_short_name(obj: dict, order_getter: Callable=None, max_key_size=None, max_value_len=MAX_VALUE_LEN):
    """
    It is responsible for
    1) get a short name without conflicts (trying to be readable)
        TODO: currently we are finding a unique prefix. If we can find the unique part, it will be better.
    2) converting the values to str
    """

    def _reverse(name):
        return ".".join(reversed(name.split(".")))

    def value2str(v):
        # 2) converting the values to str
        if isinstance(v, (list, tuple)):
            res = ",".join(str(i) for i in v)
        else:
            res = str(v)
        return res[:max_value_len]

    keys = list(obj)
    keys.sort(key=lambda k: (None if order_getter is None else order_getter(k), k.count(ARG_SEP), k.split()))  # short names come first
    keys_rev = [_reverse(k) for k in keys]
    new_dict = collections.OrderedDict()
    min_len = 2
    for k, k_rev in zip(keys, keys_rev):
        for i in range(min(min_len, len(k_rev.split(".")[0])), len(k_rev) + 1):  # TODO: make it smarter
            # 1) Don't stop at separate
            if k_rev[i - 1] == ".":
                continue

            prefix = k_rev[:i]

            # 2) Don't duplicate with other keys
            if prefix in new_dict:
                continue

            # 3) Don't be ambiguous in the unique keys (it can't be the shared prefix key)
            # FIXME: it is may be ambiguous when consindering with other keys
            if any(k.startswith(prefix)  for k in keys_rev if k != k_rev):
                continue

            # otherwise, create the key
            new_dict[prefix] = value2str(obj[k])
            break
    return ",".join(f"{_reverse(k)}={v}" for k, v in list(new_dict.items())[:max_key_size])


class NameIt:
    """
    Config and name it!!
    - config by `__init__`
    - name it by `__call__`
    """
    # TODO: get a batch of name
    def __init__(self, save=True, hist_path=HIST_PATH):
        self.save = save
        # TODO: user can config sth in the __init__ function
        self.hist_path = Path(hist_path).expanduser()
        self.hist_path.mkdir(parents=True, exist_ok=True)

    def __call__(self, *args, **kwargs) -> str:
        """
        given any objects, give it an dirty name!!!!

        Returns
        -------
        str
            the name of objects
        """
        obj = convert2basic({"args": args, "kwargs": kwargs})
        if self.save:
            with (self.hist_path / str(uuid4())).open("wb") as f:
                pickle.dump(obj, f)

        obj = flatten_obj(obj)

        # if the name is short (when including all keys), just return it directly
        name = get_short_name(obj)
        if len(name) < MAX_LEN:
            return name

        # if the name is long. Then try to find its specialness
        skip = 1 if self.save else 0  # the name itself should not be saved.
        while True:  # try to find the special part
            prev_obj_l = [flatten_obj(po) for po in self.get_prev_obj_l(skip=skip)]  # skip the one we saved just now
            # only keep the important part of object

            all_keys = set(obj.keys())
            for po in prev_obj_l:
                all_keys = set(po.keys()) | all_keys

            prev_res = collections.defaultdict(set)
            for po in prev_obj_l:
                for k in all_keys:
                    prev_res[k].add(po.get(k, NOT_APPEAR))

            # FIXME: If long value is encountered, it may result in long name
            # Solution:
            # - find the unique part of the value
            # - create a short representation based on the unique part
            uniq_info = {}
            for k, v in obj.items():
                # The new value is totally different from previous
                if len(prev_obj_l) > 0:
                    if len(prev_res[k]) > 1 or len(prev_res[k]) == 1 and next(iter(prev_res[k])) != v:
                        uniq_info[k] = v
                else:
                    uniq_info[k] = v
            if len(uniq_info) > 0:
                # Try to pick import part and put it a first;
                key_order = {}
                for k in uniq_info.keys():
                    key_order[k] = tuple(po.get(k, NOT_APPEAR) == uniq_info[k] for po in prev_obj_l)
                return get_short_name(uniq_info, order_getter=key_order.get, max_key_size=MAX_KEY_SIZE)
            skip += 1

    def get_prev_obj_l(self, skip=0):
        files = sorted(filter(lambda p: p.is_file(), self.hist_path.glob("*")), key=os.path.getctime, reverse=True)
        res = []
        for i, fp in enumerate(files[skip:]):
            if i < LIMIT:
                with fp.open("rb") as f:
                    res.append(pickle.load(f))
            else:
                fp.unlink()
        return res

    def clear_prev_obj_l(self):
        for f in self.hist_path.glob("*"):
            f.unlink()

# syntax sugar;
# - so you can call it by pn.opt(...)(obj)
opt = NameIt


class CallableModule(ModuleType):
    """Make it callable"""

    def __call__(self, *args, **kwargs):
        return opt()(*args, **kwargs)


sys.modules[__name__].__class__ = CallableModule
