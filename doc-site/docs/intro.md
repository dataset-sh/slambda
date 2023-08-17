---
title: Getting Started
sidebar_position: 1
---

# Getting Started

## Install

```bash
pip install slambda
```

## Prerequisite

Currently, sLambda only supports OpenAI's ChatCompletion API, so you will need an OpenAI API key in order to use this
package,

Please check [OpenAI's documentation: Authentication](https://platform.openai.com/docs/api-reference/authentication) if
you need to create a new API key.

If you have encountered this error:

```
AuthenticationError: No API key provided. You can set your API key in code using 'openai.api_key = <API-KEY>', 
or you can set the environment variable OPENAI_API_KEY=<API-KEY>). If your API key is stored in a file, 
you can point the openai module at it with 'openai.api_key_path = <PATH>'. You can generate API keys in the OpenAI web 
interface. See https://platform.openai.com/account/api-keys for details.
```

It means that you need to supply `OPENAI_API_KEY` somewhere in your code. Check out our guide
on [Loading API key](/docs/tips/apikey) for best practices.

```python
import os
import openai

# We highly recommend you to load OPENAI_API_KEY via environmental variable 
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------or---------

# You can also do it by providing value directly
openai.api_key = "sk-ThIsIsAFaKeKEY12345678990...."
# But we considered to be a security risk, please read our guide on how to load api key for more details. 
```

## What does slambda do?

> Wrapping the ChatGPT API call routine as a function is a frequent task that developers encounter, particularly when
needing to streamline different inference routines. To simplify this process, we have created a very basic Python
library that enables the reuse of zero-shot, one-shot, or few-shot inference routines. This library is designed with
simplicity in mind, allowing developers to utilize the declared workflow as a standard Python function. Additionally,
the library has several built-in tasks that we have identified as useful for a variety of applications, further
enhancing its practicality and ease of use.


We provide python functions for NLP tasks through zero/one/few shot learning using LLMs. For example, we heavily
use `system`, `example_user`, and `example_assistant` messages in OpenAI's ChatCompletion API.

## Start using it

```py

from slambda.contrib.sentiment import sentiment

print(sentiment('the food is great!') == 'positive')
# Output: True
```

See [Functions](/docs/category/functions) for existing function implementations.


