---
title: "Example: Simple Sentiment Classifier"
sidebar_position: 3
---

## Create TextFunction

In this example, we will create an extremly simple sentiment classifier using a `TextFunction`, so we can do this

```py
from .sl_tutorial import sentiment

print(sentiment('the food is so great!'))
# > Output: positive

print(sentiment('the food is so bad!'))
# > Output: negative
```

We can do this in two ways:
* Using a standard `Template`
* Using `Instruction` and `Examples`

### Using a standard Template

```py
# sl_tutorial.py

from slambda import TextFunction, Definition, Message

t = TextFunction(Definition(
    init_messages=[
        Message.system('Answer positive if sentence has positive general sentiment, otherwise answer negative.'),
        Message.example_user('The food is great'),
        Message.example_assistant('positive'),
        Message.example_user('The food is awful'),
        Message.example_assistant('negative'),
    ],
    tempature=0,
))
sentiment = TextFunction(t)

# Or you can use a decorator
# @TextFunction.wrap(t)
# def sentiment():
#     pass # function body will be discarded
```

###  Using Instruction And Examples

```py
# sl_tutorial.py

from slambda import Definition, Example, TextFunction

t = Definition(tempature=0).from_instruction(
    instruction="Answer positive if sentence has positive general sentiment, otherwise answer negative.",
    examples=[
        Example("The food is great", "positive"),
        Example("The food is awful", "negative")
    ]
)

sentiment = TextFunction(t)

# Or you can use a decorator
# @TextFunction.wrap(t)
# def sentiment():
#     pass # function body will be discarded

```