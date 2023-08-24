---
title: API Reference
description: Slambda API reference
sidebar_position: 4
---

# API Reference

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

```python
class TextFunctionMode(str, Enum):
    """
    TextFunctionMode control how a text function can be called.
    """
    KEYWORD = 'keyword'
    """
    KEYWORD allows calling with keyword arguments, e.g. f(a=10).
    """
    POS = 'pos'
    """
    POS allows calling with positional arguments, e.g. f(10).
    """
    NO_ARGS = 'no_args'
    """
    NO_ARGS allows calling with no arguments, e.g. f().
    """
```

```python
class Example(BaseModel):
    """
    Input and output pair example.
    The `input` field of `Example` can be one of `None`, a `str` value, or a `dict` object.

    The `output` field of `Example` can be either a `str` value, or a `dict` object.

    * For nullary function, the `input` field should be `None`.
    * For unary function, the `input` field should be `string`. If `allow_no_arg` is `True`, it can also be `None`.
    * For keyword function, the `input` field should be `dict`. If `allow_no_arg` is `True`, it can also be `None`.

    If input is a dict, all value in input.values() must be able to render as a string with f-string i.e. `f"{value}"`.

    Args:
        input: `None`, a `str` value, or a `dict` object.
        output: `str` value, or a `dict` object.
    """
    input: Optional[Union[Dict, str]] = None
    output: Union[Dict, List, str] = None
```

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
        description: an optional description for the template.
        mode: what call modes are allowed. See (TextFunctionMode)[#TextFunctionMode] for detail.
        init_messages: A list of messages comprising the conversation so far, this can be used for providing.
        default_message: this message will be sent if no args are provided.
        message_template: this message will be rendered with keyword arguments if kwargs are provided.
        required_args: list of required keyword args.
        json_output: if output is in json format or string.
        examples: call examples.
        gpt_opts: Inference parameters for ChatCompletion API.
    """
    # Template Information
    name: Optional[str] = None
    description: str = ''
    mode: List[TextFunctionMode] = Field(default_factory=list)

    # Message Config
    init_messages: List[Message] = Field(default_factory=list)
    default_message: Optional[str] = None
    message_template: Optional[str] = None
    required_args: Optional[List[str]] = None
    json_output: bool = False

    examples: List[Example] = Field(default_factory=list)

    # OpenAI parameters
    gpt_opts: GptApiOptions = Field(default_factory=GptApiOptions)
```

```python
class TextFunction:
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

```python
def create_function(
        instruction: str,
        examples: Optional[List[Example]] = None,
        gpt_opts: Optional[GptApiOptions] = None,

        allow_no_arg: bool = False,
        default_message: Optional[str] = None,

        allow_pos: bool = False,

        allow_keyword: bool = False,
        message_template: Optional[str] = None,
        required_args: Optional[List[str]] = None,

        json_output=None,
):
    """
    Create text function based on instruction and examples. We consider this to be an internal API and user should be
    using one of `NullaryFunction`, `UnaryFunction`, `KeywordFunction` instead.

    At least One of [allow_no_arg, allow_pos, allow_keyword] must be true, and allow_pos, allow_keyword cannot
    both be true.

    :param instruction: Describe what the function should do.
    :param examples: Input/Output examples.
    :param gpt_opts: Optional `GptApiOptions` to override the default inference parameters.
    :param allow_no_arg: if True, this function call be called without any parameters.
    :param default_message: if allow_no_arg, this message will be sent if no args are provided.
    :param allow_pos: if True, this function will be a unary function.
    :param allow_keyword: if True, this function will be a keyword function.
    :param message_template: if message_template is provided, it will be used to render the out-going message by running
                             `message_template.format(**kwargs)`.
                             Otherwise, value of "\n".join([f"{k}: {v}" for k, v in kwargs.items()]) will be used.
    :param required_args: list of required keyword args. If message_template is provided and required_args is None,
                          we will try to figure out this value based on the given message_template.
    :param json_output: if output is json or not. If this value is None, we will determine its value based on the
                        examples.
    :return: the defined function.
    """
```

```python
class NullaryFunction:
    """
    A function with no input argument.
    """

    def __init__(self):
        raise ValueError('Use NullaryFunction.from_instruction')

    @staticmethod
    def from_instruction(
            instruction: str,
            examples: Optional[List[Example]] = None,
            gpt_opts: Optional[GptApiOptions] = None,

            default_message: Optional[str] = None,

            json_output=None,
    ):
        """
        Create a nullary function.

        :param instruction: Describe what the function should do.
        :param examples: Input/Output examples.
        :param gpt_opts: Optional `GptApiOptions` to override the default inference parameters.
        :param default_message:  this message will be sent if no args are provided, otherwise instruction will be
                                 used as default_message.
        :param json_output: if output is json or not. If this value is None, we will determine its value based on the
                            examples.
        :return:
        """
```

```python
class UnaryFunction:
    """
    A function with exactly one positional input argument.
    """

    def __init__(self):
        raise ValueError('Use UnaryFunction.from_instruction')

    @staticmethod
    def from_instruction(
            instruction: str,
            examples: Optional[List[Example]] = None,
            gpt_opts: Optional[GptApiOptions] = None,

            allow_no_arg: bool = False,
            default_message: Optional[str] = None,

            json_output=None,
    ):
        """
        Create a unary function.
        :param instruction: Describe what the function should do.
        :param examples: Input/Output examples.
        :param gpt_opts: Optional `GptApiOptions` to override the default inference parameters.
        :param allow_no_arg: if True, this function call be called without any parameters.
        :param default_message: if allow_no_arg, this message will be sent if no args are provided.
        :param json_output: if output is json or not. If this value is None, we will determine its value based on the
                            examples.
        :return:
        """

```

```python
class KeywordFunction:
    """
    A function with only keyword input arguments.
    """

    def __init__(self):
        raise ValueError('Use KeywordFunction.from_instruction')

    @staticmethod
    def from_instruction(
            instruction: str,
            examples: Optional[List[Example]] = None,
            gpt_opts: Optional[GptApiOptions] = None,

            message_template: Optional[str] = None,

            allow_no_arg: bool = False,
            default_message: Optional[str] = None,

            json_output=None,
    ):
        """
        Create a keyword function.
        :param instruction: Describe what the function should do.
        :param examples: Input/Output examples.
        :param gpt_opts: Optional `GptApiOptions` to override the default inference parameters.
        :param message_template: if message_template is provided, it will be used to render the out-going message by running
                                 `message_template.format(**kwargs)`.
                                 Otherwise, value of "\n".join([f"{k}: {v}" for k, v in kwargs.items()]) will be used.
        :param allow_no_arg: if True, this function call be called without any parameters.
        :param default_message: if allow_no_arg, this message will be sent if no args are provided.
        :param json_output: if output is json or not. If this value is None, we will determine its value based on the
                            examples.
        :return:
        """
```
