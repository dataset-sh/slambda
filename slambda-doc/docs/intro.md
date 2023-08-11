---
title: Getting Started
sidebar_position: 1
---

# Getting Started

## Install

```bash
pip install slambda
```

### Dependencies

The only dependencies for **slambda** are
*  `pydantic >= 2.0`
*  `openai`

You will also need an OpenAI API key if you don't already have one.

## Prerequisite

Currently, sLambda only supports OpenAI's ChatCompletion API, so you will need an OpenAI API key in order to use this package,

Please check [OpenAI's documentation: Authentication](https://platform.openai.com/docs/api-reference/authentication) if you need to create a new API key.

## What does slambda do?

> With a user-friendly interface and seamless integration with popular LLMs like GPT-3, sLambda simplifies the entire few-shot learning process. Researchers, developers, and data scientists can now effortlessly use LLMs for various NLP tasks, from text classification to sentiment analysis, without the complexities of setup and coding. Experience rapid prototyping, tackle low-resource NLP challenges, and adapt sLambda to diverse domains, all while benefiting from extensive documentation, performance metrics, and a supportive community. Unlock the true potential of LLMs with sLambda and supercharge your few-shot learning endeavors.
> -- <cite>By ChatGPT</cite>
>

We provide python functions for NLP tasks through zero/one/few shot learning using LLMs. For example, we heavily use `system`, `example_user`, and `example_assistant` messages in OpenAI's ChatCompletion API.


## Start using it

```py

from slambda.contrib.sentiment import sentiment
print(sentiment('the food is great !') == 'positive')
# Output: True
```

See [Functions](/docs/category/functions) for existing function implementations.


