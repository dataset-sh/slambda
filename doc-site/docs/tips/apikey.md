---
title: OpenAI API Keys
sidebar_position: 1
---

# OpenAI API Keys

## How to get an API Key

## How to load API Key in python

### Load through Env Variable

#### Use `python-dotenv` library

Python-dotenv reads key-value pairs from a .env file and can set them as environment variables. It helps in the
development of applications following the 12-factor principles.

Install python-dotenv

```shell
pip install python-dotenv
```

Now create a file `.env.local`, and make sure you also include this in your `.gitignore` file.

```shell title=".env.local"
OPENAI_API_KEY = "sk-ThIsIsAFaKeKEY12345678990...."
```

Now we can load this value in python safely

```python
import os
import openai
from dotenv import load_dotenv

load_dotenv('.local.env')  # take environment variables from .env.

# We highly recommend you to load OPENAI_API_KEY via environmental variable 
openai.api_key = os.getenv("OPENAI_API_KEY")

```
### Directly by value (NOT Recommended)

The most straightforward approach for providing an API key is loading its value directly. However, it's important to
note that **THIS APPROACH IS HIGHLY DISCOURAGED** due to its potential to introduce numerous security vulnerabilities
over time.

For example:

* There's a heightened risk of inadvertently uploading the API key to a version control platform like Github, resulting
  in the compromise of your API key's confidentiality.

```python
import openai

openai.api_key = "sk-This_may_be_a_____SECURITY_RISK___"
# We considered to be a **SECURITY RISK**
```



