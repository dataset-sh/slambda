---
title: API Reference
description: Slambda API reference
sidebar_position: 4
---

# API Reference

## Core

### LmOutputCastingError

```python
class LmOutputCastingError(Exception):
    """
    This exception will be thrown if LM output cannot be parsed using `json.loads` and cast_to_json is True.
    """

    def __init__(self, llm_output, message="cannot cast language model output"):
        """

        :param llm_output: Text output of language model
        :param message: error message
        """
        self.llm_output = llm_output
        self.message = message
        super().__init__(self.message)
```

### FunctionInputType

```python
class FunctionInputType(str, Enum):
    """
    TextFunctionMode control how a text function can be called.
    """
    KEYWORD = 'keyword'
    """
    KEYWORD allows calling with keyword arguments, e.g. f(a=10).
    """
    UNARY = 'unary'
    """
    UNARY allows calling with one positional argument1, e.g. f(10).
    """
```

### Example

```python

FunctionInput = Union[str, Dict]
FunctionOutput = Union[str, List, Dict]
```

```python

class Example(BaseModel):
    """
    Input and output pair example.
    The `input` field of `Example` can be one of `None`, a `str` value, or a `dict` object.
    The `output` field of `Example` can be either a `str` value, a `dict`/`list` object.

    If input is a dict, all value in input.values() must be able to render as a string with f-string i.e. `f"{value}"`.

    Args:
        input: `None`, a `str` value, or a `dict` object.
        output: `str` value, or a `dict`/`list` object.
    """
    input: Optional[FunctionInput] = None
    output: FunctionOutput
```

### FunctionInputConfig

```python
class FunctionInputConfig(BaseModel):
    """
    This class determine what kinds of input args is allowed for a function
    Args:
        input_type: Keyword or UNARY.
        allow_none: True if None input is allowed.
        strict_no_args: if True, the function will be a nullary function
    """
    input_type: FunctionInputType
    allow_none: bool = False
    strict_no_args: bool = False
```

### FunctionOutputConfig

```python
class FunctionOutputConfig(BaseModel):
    """
    This class determine what kinds of output should be returned for a function
    Args:
        cast_to_json: cast the output str as json.
    """
    cast_to_json: bool = False
```

### Definition

```python
class Definition(BaseModel):
    """
    Definition of a text function.

    When executing the call, all message from init_messages will be appended to the message list, and then
        * if no arguments is provided, the default message will be appended to the message list
        * if positional argument is provided, all the positional arguments will be appended to the message list
        * if keyword arguments is provided, message_template will be rendered and appended to the message list.

    Args:
        name: optional name of this template.
        input_config: what call modes are allowed. See (TextFunctionMode)[#TextFunctionMode] for detail.
        message_template: this message will be rendered with keyword arguments if kwargs are provided.
        required_args: list of required keyword args.
        examples: call examples.
        gpt_opts: Inference parameters for ChatCompletion API.
    """
    instruction: str
    examples: List[Example]

    message_stack: List[Message]

    input_config: FunctionInputConfig
    output_config: FunctionOutputConfig

    default_args: Optional[FunctionInput] = None

    # For keyword functions
    message_template: Optional[str] = None
    required_args: Optional[List[str]] = None

    # OpenAI parameters
    gpt_opts: GptApiOptions = Field(default_factory=GptApiOptions)

    name: Optional[str] = None
```

### LmFunction

```python
class LmFunction:
    """
    A text function that call be called, the preferred way to create such function is using one of
    `NullaryFunction`, `UnaryFunction`, `KeywordFunction`.
    """

    RESERVED_KEYWORDS = ['return_json', 'extra_messages', '__override', 'return_resp_obj']
    """
    RESERVED_KEYWORDS: reserved keywords:
    return_json: parse output as json.
    extra_messages: extra messages to be carried over, it will be appended after init_messages from template but 
                    before the final message
    __override: any parameters to be override, currently you can override the following:
                    * n
                    * top_p
                    * stream
                    * stop
                    * max_tokens
                    * presence_penalty
                    * frequency_penalty
                    * logit_bias
                    * user
                (see here for details)[https://platform.openai.com/docs/api-reference/chat/create]
    return_resp_obj: if set to true, the response from ChatCompletion API will be returned directly                
    """

    definition: Definition
```

### LmFunction.create

```python
class LmFunction:
    @staticmethod
    def create(
            instruction: str,
            examples: List[Example],

            name: Optional[str] = None,
            strict_no_args: Optional[bool] = None,

            default_args: Optional[FunctionInput] = None,
            message_template: Optional[str] = None,
            required_args: Optional[List[str]] = None,
            gpt_opts: Optional[GptApiOptions] = None,
    ):
        """
        Create a LmFunction based on instruction and examples.

        :param instruction: what will this function do.
        :param examples: example input/output pairs.
        :param name: an optional name of this function.
        :param strict_no_args: if True, this function will be a nullary function, however, this value will be ignored
                               if examples contain non-None input.
        :param default_args: If this value is not None, this function can be called with no arguments, and
                             the provided value will be used as default arguments instead.
        :param message_template: this message will be rendered with keyword arguments if kwargs are provided.
        :param required_args: list of required keyword args. If this value is missing and message_template is provided,
                              we will calculate required_args based on message_template.
        :param gpt_opts: inference parameters for ChatCompletion API.
        :return: function created.
        """

```

## OpenAI API Related 
### Role
```python


class Role(str, Enum):
    """
    Role for chat message.
    https://platform.openai.com/docs/api-reference/chat/create#chat/create-role
    """
    system = 'system'
    user = 'user'
    assistant = 'assistant'
    function = 'function'
```
### Message
```python
class Message(BaseModel):
    """Chat Model Message.

    Args:
        role: (Role for chat message)[https://platform.openai.com/docs/api-reference/chat/create#chat/create-role]
        content: (The contents of the message)[https://platform.openai.com/docs/api-reference/chat/create#chat/create-content]
        name: (The name of the author of this message)[https://platform.openai.com/docs/api-reference/chat/create#chat/create-name]
    """
    role: Role
    content: str
    name: Optional[str] = None
```
### GptApiOptions
```python
class GptApiOptions(BaseModel):
    """
    GptApiOptions used in OpenAI's ChatCompletion API.
    See [OpenAI's API reference](https://platform.openai.com/docs/api-reference/chat/create)

    Args:
        model: which model to use, the model must be compatible with [OpenAI's chatCompletion API](https://platform.openai.com/docs/models/model-endpoint-compatibility)
        temperature: What sampling temperature to use, between 0 and 2. See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        n: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        top_p: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        stream: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        stop: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        max_tokens: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        presence_penalty: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        frequency_penalty: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        logit_bias: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        user: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
    """
    model: str = 'gpt-3.5-turbo'
    temperature: Optional[float] = None
    n: Optional[int] = None
    top_p: Optional[float] = None
    stream: Optional[bool] = None
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    logit_bias: Optional[Dict[int, int]] = None
    user: Optional[str] = None
```