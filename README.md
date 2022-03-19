
# Introduction

For any Python objects, give it a quick dirty name!


# Typical scenarios

## Create a name for the setting of an experiment


## create a name for a configuration


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
