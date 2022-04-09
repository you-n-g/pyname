
# Introduction

For any Python objects, give it a quick dirty name!

# Installation


```bash
# You can install wan with one of the following command

# 1) install from git repo directly
pip install git+https://github.com/you-n-g/pyname.git

# 2) TODO: pypi
```


# Typical scenarios

## Create a name for the setting of an experiment  or configuration
``` python
>>> !rm ~/.pyname/ -r   # all the history names are stored here. We remove previous logs first
>>> import pyname as pn

>>> obj = {
...     'cluster': False,
...     'cv': 'simple_split',
...     'fold_n': 5,
...     'gap': 1,
...     'hp_ver': None,
...     'market_info': False,
...     'model_param_default': 'v01',
...     'model_param_update': {
...         'batch_size': 512,
...         'eval_steps': -1,
...         'max_steps': None,
...         'max_epoch': 50,
...         'lr': 0.0005,
...         'shuffle_train': False,
...         'early_stop_rounds': 5,
...         'scheduler': None
...     },
...     'no_shuffle': False,
... }

>>> print(pn(obj))  # pick several keys and generate a name
cl=False,cv=simple_split,fo=5,ga=1,hp=None

>>> obj["no_shuffle"] = True  # change part of the config
>>> print(pn(obj))  # then it will use the most important config for the name
no=True

>>> obj["gap"] = 10  # change part of the config
>>> print(pn(obj))  # the latest different config will come first
ga=10,no=True

>>> print(pn(obj, foo=10))  # you can pass in arguments directly
fo=10,ga=10,no=True
```


# How it works
It follows the following steps.
- Create a basic object based on the object (e.g. the NameSpace object created by `argparse` will be converted to dict)
- then create a name based on it.
- the previous names will be recorded. `pyname` will try best to give a short name based on the difference and hide trival part.



# Known limitations
Currently, following cases are NOT considered.
- make sure that the names are not conflicted
- make sure that the names from different machines make sense
- the name will based on previous results of `pyname`, so we can't ensure that the returned name remains the same when users call it each time.
