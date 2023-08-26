from unittest import TestCase

from slambda import Definition, LmFunction, Example, Message
from slambda.core import FunctionInputConfig, FunctionInputType, FunctionOutputConfig


class TestDefinition(TestCase):

    def test_create_message_stack_failed(self):
        with self.assertRaises(AssertionError) as ctx:
            Definition.create_message_stack(
                instruction='do this',
                examples=[
                    "",
                    Example('a1', 'b1')
                ],
                input_config=FunctionInputConfig(input_type=FunctionInputType.UNARY),
                output_config=FunctionOutputConfig(),
                default_args=None,
                required_args=None,
                message_template=None,
            )

    def test_create_message_stack(self):
        msg = Definition.create_message_stack(
            instruction='do this',
            examples=[
                Example('a', 'b'),
                Example('a1', 'b1')
            ],
            input_config=FunctionInputConfig(input_type=FunctionInputType.UNARY),
            output_config=FunctionOutputConfig(),
            default_args=None,
            required_args=None,
            message_template=None,
        )

        self.assertListEqual([
            Message.system('do this'),
            Message.example_user('a'),
            Message.example_assistant('b'),
            Message.example_user('a1'),
            Message.example_assistant('b1'),
        ], msg)

    def test_create_message_stack_kw(self):
        msg = Definition.create_message_stack(
            instruction='do this',
            examples=[
                Example({'k1': 'v1', 'k2': 'v2'}, 'b'),
                Example({'k1': 'v2', 'k2': 'v3'}, 'b1'),
            ],
            input_config=FunctionInputConfig(input_type=FunctionInputType.KEYWORD),
            output_config=FunctionOutputConfig(),
            default_args=None,
            required_args=None,
            message_template=None,
        )
        self.assertListEqual([
            Message.system('do this'),
            Message.example_user('k1: v1\nk2: v2'),
            Message.example_assistant('b'),
            Message.example_user('k1: v2\nk2: v3'),
            Message.example_assistant('b1'),
        ], msg)

        msg = Definition.create_message_stack(
            instruction='do this',
            examples=[
                Example({'k1': 'v1', 'k2': 'v2'}, 'b'),
                Example({'k1': 'v2', 'k2': 'v3'}, 'b1'),
            ],
            input_config=FunctionInputConfig(input_type=FunctionInputType.KEYWORD),
            output_config=FunctionOutputConfig(),
            default_args=None,
            required_args=None,
            message_template='{k1}, {k2}'
        )

        self.assertListEqual([
            Message.system('do this'),
            Message.example_user('v1, v2'),
            Message.example_assistant('b'),
            Message.example_user('v2, v3'),
            Message.example_assistant('b1'),
        ], msg)

    def test_definition_create_allow_none_failed(self):
        instruction = 'do this'
        examples = [Example(input={'a': 1}, output='hello')]

        with self.assertWarns(UserWarning):
            created_fn = LmFunction.create(
                instruction=instruction,
                examples=examples,
                strict_no_args=True,
            )

    def test_definition_create(self):
        instruction = 'do this'
        examples = [Example(input={'a': 1}, output='hello')]

        created_fn = LmFunction.create(
            instruction=instruction,
            examples=examples,
        )

        expected_def = Definition(
            instruction='do this',
            examples=[Example(input={'a': 1}, output='hello')],
            input_config=FunctionInputConfig(input_type=FunctionInputType.KEYWORD, allow_none=False),
            output_config=FunctionOutputConfig(),
            message_stack=[
                Message.system('do this'),
                Message.example_user('a: 1'),
                Message.example_assistant('hello'),
            ]
        )

        self.assertEqual(created_fn.definition, expected_def)

    def test_definition_create_required_args_extraction(self):
        instruction = 'do this'
        examples = [
            Example(input={'a': 1}, output='hello'),
            Example(input={'a': 1, "b": 2}, output='hello')
        ]

        with self.assertRaises(ValueError):
            LmFunction.create(
                instruction=instruction,
                examples=examples,
                required_args=['a', 'b']
            )

        created_fn = LmFunction.create(
            instruction=instruction,
            examples=examples,
            message_template='{a}: done'
        )

        expected_def = Definition(
            instruction='do this',
            examples=[
                Example(input={'a': 1}, output='hello'),
                Example(input={'a': 1, "b": 2}, output='hello')
            ],
            input_config=FunctionInputConfig(input_type=FunctionInputType.KEYWORD, allow_none=False),
            output_config=FunctionOutputConfig(),
            message_stack=[
                Message.system('do this'),
                Message.example_user('1: done'),
                Message.example_assistant('hello'),
                Message.example_user('1: done'),
                Message.example_assistant('hello'),

            ],
            required_args=['a'],
            message_template='{a}: done',
        )

        self.assertEqual(created_fn.definition, expected_def)

    def test_definition_create_nullary(self):
        instruction = 'do this'
        examples = [Example(output='hello')]

        created_fn = LmFunction.create(
            instruction=instruction,
            examples=examples,
            default_args={'a': 1},
            strict_no_args=True,
        )

        expected_def = Definition(
            instruction=instruction,
            examples=examples,
            input_config=FunctionInputConfig.nullary_keyword(),
            output_config=FunctionOutputConfig(),
            default_args={'a': 1},
            message_stack=[
                Message.system('do this'),
                Message.example_user('a: 1'),
                Message.example_assistant('hello'),
            ]
        )

        self.assertEqual(created_fn.definition, expected_def)

    def test_definition_create_nullary_pos(self):
        instruction = 'do this'
        examples = [Example(output='hello')]

        created_fn = LmFunction.create(
            instruction=instruction,
            examples=examples,
            default_args='a',
            strict_no_args=True,
        )

        expected_def = Definition(
            instruction=instruction,
            examples=examples,
            input_config=FunctionInputConfig.nullary_pos(),
            output_config=FunctionOutputConfig(),
            default_args='a',
            message_stack=[
                Message.system('do this'),
                Message.example_user('a'),
                Message.example_assistant('hello'),
            ]
        )

        self.assertEqual(created_fn.definition, expected_def)
