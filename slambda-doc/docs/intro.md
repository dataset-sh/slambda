---
title: Getting Started
sidebar_position: 1
---

# Getting Started

## Install

```bash
pip install slambda
```

## What does slambda do?

```

```

## APIs

### Template

### TextFunction

```py
from slambda import TextFunction, Template
my_function = TextFunction(Template(default_message=''))
my_function()
```
#### Calling Mode: No Args
#### Calling Mode: Positional Args
#### Calling Mode: Keyword Args

##### Reserved Keywords
The following keywords are reserved for special purposes:

```
n: How many response to sample from openai api
return_dict: Return the entire openai response object
extra_messages: extra messages to be carried over
```


### decorator

You can also define a slambda TextFunction using a decorator:
```py
from slambda import TextFunction, Template

@TextFunction.wrap(Template(default_message=''))
def my_function():
    pass # function body will be discarded


# Whihc is equivalent to
# my_function = TextFunction(Template(default_message=''))

my_function()
```
