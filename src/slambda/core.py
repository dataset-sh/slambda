import json
import warnings
from dataclasses import dataclass

import openai

from typing import Optional, List, Union, Dict, Tuple
from pydantic import BaseModel, Field
from enum import Enum

from .gpt import Message, GptApiOptions
from .utils import extract_required_keywords, try_parse_json

FunctionInput = Union[str, Dict]
FunctionOutput = Union[str, List, Dict]


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

    @staticmethod
    def of_value(input_args: Optional[FunctionInput], strict=True) -> Optional['FunctionInputType']:
        if isinstance(input_args, str):
            if strict and input_args == '':
                return None
            return FunctionInputType.UNARY
        elif isinstance(input_args, dict):
            if strict and input_args == {}:
                return None
            return FunctionInputType.KEYWORD
        elif input_args is None:
            return None
        else:
            raise ValueError('input vaule must be one of None, str, dict')


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

    @staticmethod
    def unary(allow_none: bool):
        return FunctionInputConfig(
            input_type=FunctionInputType.UNARY,
            allow_none=allow_none,
            strict_no_args=False,
        )

    @staticmethod
    def keyword(allow_none: bool):
        return FunctionInputConfig(
            input_type=FunctionInputType.KEYWORD,
            allow_none=allow_none,
            strict_no_args=False,
        )

    @staticmethod
    def nullary_keyword():
        return FunctionInputConfig(
            input_type=FunctionInputType.KEYWORD,
            allow_none=True,
            strict_no_args=True,
        )

    @staticmethod
    def nullary_pos():
        return FunctionInputConfig(
            input_type=FunctionInputType.UNARY,
            allow_none=True,
            strict_no_args=True,
        )


class FunctionOutputConfig(BaseModel):
    """
    This class determine what kinds of output should be returned for a function
    Args:
        cast_to_json: cast the output str as json.
    """
    cast_to_json: bool = False


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

    def __init__(self, input=None, output=None, **kwargs):
        super().__init__(input=input, output=output, **kwargs)

    @property
    def input_type(self) -> Optional[FunctionInputType]:
        return FunctionInputType.of_value(self.input)


@dataclass
class InputCounter:
    KEYWORD: int = 0
    POS: int = 0
    NONE: int = 0

    def count(self, input_value: Optional[FunctionInput]):
        t = FunctionInputType.of_value(input_value)
        if t is None:
            self.NONE += 1
        elif t == FunctionInputType.UNARY:
            self.POS += 1
        elif t == FunctionInputType.KEYWORD:
            self.KEYWORD += 1

    def to_config(
            self,
            default_args: Optional[FunctionInput] = None,
            strict_no_args: bool = True,
    ) -> FunctionInputConfig:
        """

        :param default_args: if default_args are provided, and has no typing conflict with examples, we will allow none.
        :param strict_no_args: if this is set to True and all examples has None as input, the function
                               will be a nullary function.
        :return:
        """
        cond = (self.has_keyword, self.has_positional, self.has_none)
        default_args_type = FunctionInputType.of_value(default_args)
        if cond == (True, True, True):
            # Keyword, Unary, and None
            raise ValueError('Example list contains both keyword and unary input.')
        elif cond == (True, True, False):
            # Keyword and Unary
            raise ValueError('Example list contains both keyword and unary input.')
        elif cond == (True, False, True):
            # Keyword and None
            if default_args_type != FunctionInputType.KEYWORD:
                raise ValueError(
                    f'default_args and example input type differ({default_args_type} != {FunctionInputType.KEYWORD}).')
            return FunctionInputConfig.keyword(True)
        elif cond == (True, False, False):
            # Has only keyword
            # if default args is provided, we will allow none
            return FunctionInputConfig.keyword(default_args_type == FunctionInputType.KEYWORD)
        elif cond == (False, True, True):
            # Has positional and None
            if default_args_type != FunctionInputType.UNARY:
                raise ValueError(
                    f'default_args and example input type differ({default_args_type} != {FunctionInputType.UNARY}).')
            return FunctionInputConfig.unary(True)
        elif cond == (False, True, False):
            # Has only positional
            # if default args is provided, we will allow none
            return FunctionInputConfig.unary(default_args_type == FunctionInputType.UNARY)
        elif cond == (False, False, True):
            # Only None input, we will determine input type using default args.
            if default_args_type == FunctionInputType.KEYWORD:
                if strict_no_args:
                    return FunctionInputConfig.nullary_keyword()
                else:
                    return FunctionInputConfig.keyword(True)
            elif default_args_type == FunctionInputType.UNARY:
                if strict_no_args:
                    return FunctionInputConfig.nullary_pos()
                else:
                    return FunctionInputConfig.unary(True)
            elif default_args_type is None:
                raise ValueError('You must provide default args for Nullary function.')
        elif cond == (False, False, False):
            raise ValueError('No example input observed')

    @property
    def has_keyword(self):
        return self.KEYWORD > 0

    @property
    def has_none(self):
        return self.NONE > 0

    @property
    def has_positional(self):
        return self.POS > 0


@dataclass
class OutputCounter:
    str_count: int = 0
    json_count: int = 0

    def count(self, output_value: FunctionOutput):
        if isinstance(output_value, str):
            self.str_count += 1
        elif isinstance(output_value, dict) or isinstance(output_value, List):
            self.json_count += 1
        else:
            raise ValueError("output_value must be str, dict or list")

    def to_config(self) -> FunctionOutputConfig:
        ret = FunctionOutputConfig()

        cond = (self.has_json, self.has_str)
        if cond == (True, True):
            raise ValueError('Example list contains both string and dict outputs.')
        elif cond == (True, False):
            # json only
            ret.cast_to_json = True
        elif cond == (False, True):
            # str only
            ret.cast_to_json = False
        else:
            raise ValueError('No example output observed.')
        return ret

    @property
    def has_json(self) -> bool:
        return self.json_count > 0

    @property
    def has_str(self) -> bool:
        return self.str_count > 0


class Definition(BaseModel):
    """

    Definition of a LmFunction, this should be created using LmFunction.create function.

    Args:
        instruction: what will this function do.
        examples: example input/output pairs.
        name: an optional name of this function.
        message_stack: created message stack to be sent to ChatCompletion API.
        input_config: this determine what input arguments are allowed
        output_config: this determine if the output of this function is a string or json object.
        default_args: If this value is not None, this function can be called with no arguments, and
                      the provided value will be used as default arguments instead.
        message_template: this message will be rendered with keyword arguments if kwargs are provided.
        required_args: list of required keyword args. If this value is missing and message_template is provided,
                       we will calculate required_args based on message_template.
        gpt_opts: inference parameters for ChatCompletion API.
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

    @staticmethod
    def create_message_stack(
            instruction: str,
            examples: List[Example],
            input_config: FunctionInputConfig,
            output_config: FunctionOutputConfig,
            default_args: Optional[str],
            required_args: Optional[List[str]],
            message_template: Optional[str]
    ) -> List[Message]:
        message_stack = [
            Message.system(instruction)
        ]

        if examples is not None:
            for example in examples:
                assert isinstance(example, Example), "example must be an instance of Example"

                input_ = Definition.render_input(
                    input_config,
                    example.input,
                    default_args,
                    required_args,
                    message_template
                )
                output = Definition.render_output_example(
                    output_config,
                    example.output
                )

                message_stack.append(
                    Message.example_user(input_)
                )
                message_stack.append(
                    Message.example_assistant(output)
                )

        return message_stack

    @staticmethod
    def render_input(
            input_config: FunctionInputConfig,
            input_arg: Optional[FunctionInput],
            default_args: Optional[FunctionInput],
            required_args: Optional[List[str]],
            message_template: Optional[str]
    ):
        if input_config.input_type == FunctionInputType.KEYWORD:
            if input_arg is None or len(input_arg) == 0:
                if default_args is not None:
                    input_arg = default_args
                else:
                    raise ValueError("default_args is missing")

            if not isinstance(input_arg, dict):
                raise ValueError(f"function input must be a dict object for this function")

            if required_args is not None:
                for key in required_args:
                    if key not in input_arg:
                        raise ValueError(f'{key} is required but not provided')

            if message_template is not None:
                return message_template.format(**input_arg)
            else:
                return "\n".join([f"{k}: {v}" for k, v in input_arg.items()])
        elif input_config.input_type == FunctionInputType.UNARY:
            if input_arg is None:
                if default_args is not None:
                    input_arg = default_args
                else:
                    raise ValueError("default_args is missing")

            if isinstance(input_arg, str):
                return input_arg
            else:
                raise ValueError(f"function input must be a str for this function")

    @staticmethod
    def render_output_example(output_config: FunctionOutputConfig, example_output: FunctionOutput) -> str:
        if output_config.cast_to_json:
            if isinstance(example_output, list) or isinstance(example_output, dict):
                return json.dumps(example_output)
            else:
                raise ValueError("example output must be a dict or list, or set fn_output_type.cast_to_json to False")
        else:
            if isinstance(example_output, str):
                return example_output
            else:
                raise ValueError("example output must be string, or set fn_output_type.cast_to_json to True")

    @staticmethod
    def cast_lm_output(output_config: FunctionOutputConfig, llm_output: str) -> Union[List, Dict]:
        if output_config.cast_to_json:
            json_value, parsed = try_parse_json(llm_output)
            if parsed:
                return json_value
            else:
                raise LmOutputCastingError(llm_output=llm_output)
        else:
            return llm_output

    @staticmethod
    def detect_input_output_type(
            examples: List['Example'],
            default_args: Optional[FunctionInput] = None,
            strict_no_args: bool = False,
    ) -> Tuple[FunctionInputConfig, FunctionOutputConfig]:
        """

        :param examples:
        :param default_args: if default_args is provided and has no typing conflict, allow_none will be true
        :param strict_no_args:
        :return:
        """

        if len(examples) == 0:
            raise ValueError('No examples are provided.')

        observed_inputs = InputCounter()
        observed_outputs = OutputCounter()

        for example in examples:
            observed_inputs.count(example.input)
            observed_outputs.count(example.output)

        return (
            observed_inputs.to_config(default_args=default_args, strict_no_args=strict_no_args),
            observed_outputs.to_config()
        )


class LmFunction:
    """
    A text function that call be called, the preferred way to create such function is using one of
    `NullaryFunction`, `UnaryFunction`, `KeywordFunction`.
    """

    RESERVED_KEYWORDS = ['__extra_messages', '__override', '__return_resp_obj']
    """
    RESERVED_KEYWORDS: reserved keywords:
    __extra_messages: extra messages to be carried over, it will be appended after instruction and examples but 
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
    __return_resp_obj: if set to true, the response from ChatCompletion API will be returned directly                
    """

    definition: Definition

    def __init__(self, definition):
        self.definition = definition

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
                               if examples contains non-None input.
        :param default_args: If this value is not None, this function can be called with no arguments, and
                             the provided value will be used as default arguments instead.
        :param message_template: this message will be rendered with keyword arguments if kwargs are provided.
        :param required_args: list of required keyword args. If this value is missing and message_template is provided,
                              we will calculate required_args based on message_template.
        :param gpt_opts: inference parameters for ChatCompletion API.
        :return: function created.
        """

        (fn_input_type, fn_output_type) = Definition.detect_input_output_type(
            examples,
            default_args=default_args,
            strict_no_args=strict_no_args
        )

        if not fn_input_type.strict_no_args and strict_no_args is True:
            warnings.warn("strict_no_args flag is ignored")

        if message_template is not None:
            if required_args is None:
                required_args = extract_required_keywords(message_template)

        if gpt_opts is None:
            gpt_opts = GptApiOptions()

        message_stack = Definition.create_message_stack(
            instruction=instruction,
            examples=examples,
            input_config=fn_input_type,
            output_config=fn_output_type,
            default_args=default_args,
            required_args=required_args,
            message_template=message_template,
        )

        t = Definition(
            name=name,
            instruction=instruction,
            examples=examples,
            message_stack=message_stack,

            input_config=fn_input_type,
            output_config=fn_output_type,

            default_args=default_args,

            message_template=message_template,
            required_args=required_args,

            gpt_opts=gpt_opts,
        )

        return LmFunction(t)

    def __call__(self, *args, **kwargs):
        """
        Execute the function call based on the provided template

        :param args:
        :param kwargs:
        :return:
        """
        all_kwargs = kwargs
        kwargs = {}
        ctrl_kws = {}
        for k, v in all_kwargs.items():
            if k in LmFunction.RESERVED_KEYWORDS:
                ctrl_kws[k] = v
            else:
                kwargs[k] = v

        extra_msgs = ctrl_kws.get('__extra_messages', [])

        fn_input_args = None
        if self.definition.input_config.input_type == FunctionInputType.KEYWORD:
            if self.definition.input_config.strict_no_args:
                if len(args) > 0:
                    raise ValueError('received positional arguments for nullary function.')
                if len(kwargs) > 0:
                    raise ValueError('received keyword arguments for nullary function.')
            else:
                if len(kwargs) > 0:
                    fn_input_args = kwargs
                else:
                    fn_input_args = None
        elif self.definition.input_config.input_type == FunctionInputType.UNARY:
            if self.definition.input_config.strict_no_args:
                if len(args) > 0:
                    raise ValueError('received positional arguments for nullary function.')
                if len(kwargs) > 0:
                    raise ValueError('received keyword arguments for nullary function.')
            else:
                if len(kwargs) > 0:
                    raise ValueError('received keyword arguments for unary function.')

                if len(args) == 0:
                    fn_input_args = None
                elif len(args) == 1:
                    fn_input_args = args[0]
                else:
                    raise ValueError('received more than 1 positional arguments.')

        messages = [m for m in self.definition.message_stack]

        if extra_msgs is not None:
            for m in extra_msgs:
                if not isinstance(m, Message):
                    raise ValueError('message in extra_messages must be an instance of slambda.Message')
                messages.append(m)

        messages.append(
            Message.user(Definition.render_input(
                self.definition.input_config,
                fn_input_args,
                self.definition.default_args,
                self.definition.required_args,
                self.definition.message_template
            ))
        )

        override_params = ctrl_kws.get('__override', {})

        model = override_params.get('model', self.definition.gpt_opts.model)
        n = override_params.get('n', self.definition.gpt_opts.n)
        temperature = override_params.get('temperature', self.definition.gpt_opts.temperature)
        top_p = override_params.get('top_p', self.definition.gpt_opts.top_p)
        stream = override_params.get('stream', self.definition.gpt_opts.stream)
        stop = override_params.get('stop', self.definition.gpt_opts.stop)
        max_tokens = override_params.get('max_tokens', self.definition.gpt_opts.max_tokens)
        presence_penalty = override_params.get('presence_penalty', self.definition.gpt_opts.presence_penalty)
        frequency_penalty = override_params.get('frequency_penalty', self.definition.gpt_opts.frequency_penalty)
        logit_bias = override_params.get('logit_bias', self.definition.gpt_opts.logit_bias)
        user = override_params.get('user', self.definition.gpt_opts.user)

        call_args_dict = dict(
            messages=[
                m.model_dump(exclude_none=True, mode='json') for m in messages
            ],
            model=model,
            n=n,
            temperature=temperature,
            top_p=top_p,
            stream=stream,
            stop=stop,
            max_tokens=max_tokens,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            logit_bias=logit_bias,
            user=user
        )

        call_args_dict = {k: v for k, v in call_args_dict.items() if v is not None}
        resp = openai.ChatCompletion.create(**call_args_dict)

        return_resp_obj = ctrl_kws.get('__return_resp_obj', False) or stream is True
        if return_resp_obj:
            return resp

        if n is None or n == 1:
            ret = resp['choices'][0]['message']['content']
            return Definition.cast_lm_output(self.definition.output_config, ret)
        else:
            return [Definition.cast_lm_output(self.definition.output_config, c['message']['content']) for c in
                    resp['choices']]
