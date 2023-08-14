# Sλ

Wrapping the ChatGPT API call routine as a function is a frequent task that developers encounter, particularly when
needing to streamline different inference routines. To simplify this process, we have created a very basic Python
library that enables the reuse of zero-shot, one-shot, or few-shot inference routines. This library is designed with
simplicity in mind, allowing developers to utilize the declared workflow as a standard Python function. Additionally,
the library has several built-in tasks that we have identified as useful for a variety of applications, further
enhancing its practicality and ease of use.

## Install

```bash
pip install slambda
```

## Start using it

```py

from slambda.contrib.sentiment import sentiment

print(sentiment('the food is great !') == 'positive')
# Output: True
```

See [Functions](https://slambda.dataset.sh/docs/category/functions) for existing function implementations.

## Documentation

See (Documentation)[https://slambda.dataset.sh]
