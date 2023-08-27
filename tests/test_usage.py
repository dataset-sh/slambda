from unittest import TestCase, mock
from unittest.mock import call

from slambda import LmFunction, Example, GptApiOptions, Message


def gpt_text(**kwargs):
    choices = []
    for i in range(kwargs.get('n', 1)):
        choices.append(
            {
                'message': {
                    'content': f"v{i}"
                }
            }
        )
    return dict(choices=choices)


def gpt_list(**kwargs):
    choices = []
    for i in range(kwargs.get('n', 1)):
        choices.append(
            {
                'message': {
                    'content': f'[{{"k1": "v{i}"}}, {{"k2": "v{i}"}}]'
                }
            }
        )
    return dict(choices=choices)


def gpt_dict(**kwargs):
    choices = []
    for i in range(kwargs.get('n', 1)):
        choices.append(
            {
                'message': {
                    'content': f'{{"k1": "v{i}"}}'
                }
            }
        )
    return dict(choices=choices)


class TestLogEntryController(TestCase):
    @mock.patch('openai.ChatCompletion.create')
    def test_nullary(self, mock_openai_api):
        mock_openai_api.side_effect = gpt_text
        f = LmFunction.create(
            'do this',
            examples=[
                Example(output='v1'),
                Example(output='v2'),
            ],
            default_args='g',
            strict_no_args=True
        )
        o = f()
        self.assertEqual('v0', o)

        self.assertEqual(1, len(mock_openai_api.call_args_list))
        call_args = call(messages=[{'role': 'system', 'content': 'do this'},
                                   {'role': 'system', 'content': 'g', 'name': 'example_user'},
                                   {'role': 'system', 'content': 'v1', 'name': 'example_assistant'},
                                   {'role': 'system', 'content': 'g', 'name': 'example_user'},
                                   {'role': 'system', 'content': 'v2', 'name': 'example_assistant'},
                                   {'role': 'user', 'content': 'g'}], model='gpt-3.5-turbo')
        self.assertEqual(
            call_args, mock_openai_api.call_args_list[-1]
        )

        with self.assertRaises(ValueError):
            f('?')

        with self.assertRaises(ValueError):
            f(a=10)

    @mock.patch('openai.ChatCompletion.create')
    def test_nullary_kw(self, mock_openai_api):
        mock_openai_api.side_effect = gpt_text
        f = LmFunction.create(
            'do this',
            examples=[
                Example(output='v1'),
                Example(output='v2'),
            ],
            default_args={'g': 1},
            strict_no_args=True
        )

        o = f()
        self.assertEqual('v0', o)

        self.assertEqual(1, len(mock_openai_api.call_args_list))
        call_args = call(messages=[{'role': 'system', 'content': 'do this'},
                                   {'role': 'system', 'content': 'g: 1', 'name': 'example_user'},
                                   {'role': 'system', 'content': 'v1', 'name': 'example_assistant'},
                                   {'role': 'system', 'content': 'g: 1', 'name': 'example_user'},
                                   {'role': 'system', 'content': 'v2', 'name': 'example_assistant'},
                                   {'role': 'user', 'content': 'g: 1'}], model='gpt-3.5-turbo')
        self.assertEqual(
            call_args, mock_openai_api.call_args_list[-1]
        )

        with self.assertRaises(ValueError):
            f('?')

        with self.assertRaises(ValueError):
            f(a=10)

    @mock.patch('openai.ChatCompletion.create')
    def test_unary(self, mock_openai_api):
        mock_openai_api.side_effect = gpt_text
        f = LmFunction.create(
            'do this',
            examples=[
                Example(input="i0", output='v1'),
                Example(input="i1", output='v2'),
            ]
        )

        o = f('as')
        self.assertEqual('v0', o)

        self.assertEqual(1, len(mock_openai_api.call_args_list))
        call_args = call(messages=[{'role': 'system', 'content': 'do this'},
                                   {'role': 'system', 'content': 'i0', 'name': 'example_user'},
                                   {'role': 'system', 'content': 'v1', 'name': 'example_assistant'},
                                   {'role': 'system', 'content': 'i1', 'name': 'example_user'},
                                   {'role': 'system', 'content': 'v2', 'name': 'example_assistant'},
                                   {'role': 'user', 'content': 'as'}], model='gpt-3.5-turbo')
        self.assertEqual(
            call_args, mock_openai_api.call_args_list[-1]
        )

        with self.assertRaises(ValueError):
            f()
        with self.assertRaises(ValueError):
            f('1', '2')

        with self.assertRaises(ValueError):
            f(a=10)

    @mock.patch('openai.ChatCompletion.create')
    def test_unary_allow_none(self, mock_openai_api):
        mock_openai_api.side_effect = gpt_text
        f = LmFunction.create(
            'do this',
            examples=[
                Example(input="i0", output='v1'),
                Example(input="i1", output='v2'),
            ],
            default_args='?'
        )
        o = f('as')
        self.assertEqual('v0', o)

        self.assertEqual(1, len(mock_openai_api.call_args_list))
        call_args = call(messages=[{'role': 'system', 'content': 'do this'},
                                   {'role': 'system', 'content': 'i0', 'name': 'example_user'},
                                   {'role': 'system', 'content': 'v1', 'name': 'example_assistant'},
                                   {'role': 'system', 'content': 'i1', 'name': 'example_user'},
                                   {'role': 'system', 'content': 'v2', 'name': 'example_assistant'},
                                   {'role': 'user', 'content': 'as'}], model='gpt-3.5-turbo')
        self.assertEqual(
            call_args, mock_openai_api.call_args_list[-1]
        )

        with self.assertRaises(ValueError):
            f(a=10)

        o = f()
        self.assertEqual('v0', o)
        self.assertEqual(2, len(mock_openai_api.call_args_list))
        call_args = call(messages=[{'role': 'system', 'content': 'do this'},
                                   {'role': 'system', 'content': 'i0', 'name': 'example_user'},
                                   {'role': 'system', 'content': 'v1', 'name': 'example_assistant'},
                                   {'role': 'system', 'content': 'i1', 'name': 'example_user'},
                                   {'role': 'system', 'content': 'v2', 'name': 'example_assistant'},
                                   {'role': 'user', 'content': '?'}], model='gpt-3.5-turbo')
        self.assertEqual(
            call_args, mock_openai_api.call_args_list[-1]
        )

    @mock.patch('openai.ChatCompletion.create')
    def test_keyword(self, mock_openai_api):
        mock_openai_api.side_effect = gpt_text
        f = LmFunction.create(
            'do this',
            examples=[
                Example(input={"k1": 'v1'}, output='v1'),
                Example(input={"k1": 'v2'}, output='v2'),
            ],
            default_args={'k1': 'v'}
        )

        o = f()
        call_args = call(messages=[{'role': 'system', 'content': 'do this'},
                                   {'role': 'system', 'content': 'k1: v1', 'name': 'example_user'},
                                   {'role': 'system', 'content': 'v1', 'name': 'example_assistant'},
                                   {'role': 'system', 'content': 'k1: v2', 'name': 'example_user'},
                                   {'role': 'system', 'content': 'v2', 'name': 'example_assistant'},
                                   {'role': 'user', 'content': 'k1: v'}], model='gpt-3.5-turbo')
        self.assertEqual(
            call_args, mock_openai_api.call_args_list[-1]
        )

        o = f(k1=12)
        call_args = call(messages=[{'role': 'system', 'content': 'do this'},
                                   {'role': 'system', 'content': 'k1: v1', 'name': 'example_user'},
                                   {'role': 'system', 'content': 'v1', 'name': 'example_assistant'},
                                   {'role': 'system', 'content': 'k1: v2', 'name': 'example_user'},
                                   {'role': 'system', 'content': 'v2', 'name': 'example_assistant'},
                                   {'role': 'user', 'content': 'k1: 12'}], model='gpt-3.5-turbo')
        self.assertEqual(
            call_args, mock_openai_api.call_args_list[-1]
        )

    @mock.patch('openai.ChatCompletion.create')
    def test_keyword_allow_none(self, mock_openai_api):
        mock_openai_api.side_effect = gpt_text
        f = LmFunction.create(
            'do this',
            examples=[
                Example(input={"k1": 'v1'}, output='v1'),
                Example(input={"k1": 'v2'}, output='v2'),
            ],
            default_args={'k1': 'v'}
        )

    @mock.patch('openai.ChatCompletion.create')
    def test_json_dict_output(self, mock_openai_api):
        mock_openai_api.side_effect = gpt_dict
        f = LmFunction.create(
            'do this',
            examples=[
                Example(input={"k1": 'v1'}, output={'k1': 'vvv'}),
                Example(input={"k1": 'v2'}, output={'k1': 'vvvvv'}),
            ],
            default_args={'k1': 'v'}
        )

        v = f()
        self.assertEqual({'k1': 'v0'}, v)

    @mock.patch('openai.ChatCompletion.create')
    def test_json_list_output(self, mock_openai_api):
        mock_openai_api.side_effect = gpt_list
        f = LmFunction.create(
            'do this',
            examples=[
                Example(input={"k1": 'v1'}, output=[{'k1': 'vvv'}]),
                Example(input={"k1": 'v2'}, output=[{'k1': 'vvvvv'}]),
            ],
            default_args={'k1': 'v'}
        )

        v = f()
        self.assertEqual([{'k1': 'v0'}, {'k2': 'v0'}], v)

    @mock.patch('openai.ChatCompletion.create')
    def test_override(self, mock_openai_api):
        mock_openai_api.side_effect = gpt_text
        f = LmFunction.create(
            'do this',
            examples=[
                Example(input={"k1": 'v1'}, output='v1'),
                Example(input={"k1": 'v2'}, output='v2'),
            ],
            default_args={'k1': 'v'},
            gpt_opts=GptApiOptions(temperature=0.5)
        )

        o = f(__override={'temperature': 0.9})
        call_args = call(
            temperature=0.9,
            messages=[{'role': 'system', 'content': 'do this'},
                      {'role': 'system', 'content': 'k1: v1', 'name': 'example_user'},
                      {'role': 'system', 'content': 'v1', 'name': 'example_assistant'},
                      {'role': 'system', 'content': 'k1: v2', 'name': 'example_user'},
                      {'role': 'system', 'content': 'v2', 'name': 'example_assistant'},
                      {'role': 'user', 'content': 'k1: v'}], model='gpt-3.5-turbo')
        self.assertEqual(
            call_args, mock_openai_api.call_args_list[-1]
        )

    @mock.patch('openai.ChatCompletion.create')
    def test_customized_gpt_para(self, mock_openai_api):
        mock_openai_api.side_effect = gpt_text
        f = LmFunction.create(
            'do this',
            examples=[
                Example(input={"k1": 'v1'}, output='v1'),
                Example(input={"k1": 'v2'}, output='v2'),
            ],
            default_args={'k1': 'v'},
            gpt_opts=GptApiOptions(temperature=0.5)
        )

        o = f()
        call_args = call(
            temperature=0.5,
            messages=[{'role': 'system', 'content': 'do this'},
                      {'role': 'system', 'content': 'k1: v1', 'name': 'example_user'},
                      {'role': 'system', 'content': 'v1', 'name': 'example_assistant'},
                      {'role': 'system', 'content': 'k1: v2', 'name': 'example_user'},
                      {'role': 'system', 'content': 'v2', 'name': 'example_assistant'},
                      {'role': 'user', 'content': 'k1: v'}], model='gpt-3.5-turbo')
        self.assertEqual(
            call_args, mock_openai_api.call_args_list[-1]
        )

    @mock.patch('openai.ChatCompletion.create')
    def test_extra_message(self, mock_openai_api):
        mock_openai_api.side_effect = gpt_text
        f = LmFunction.create(
            'do this',
            examples=[
                Example(input={"k1": 'v1'}, output='v1'),
                Example(input={"k1": 'v2'}, output='v2'),
            ],
            default_args={'k1': 'v'},
            gpt_opts=GptApiOptions(temperature=0.5)
        )

        o = f(__extra_messages=[
            Message.user('hello'),
            Message.user('hello2'),
        ])
        call_args = call(
            temperature=0.5,
            messages=[{'role': 'system', 'content': 'do this'},
                      {'role': 'system', 'content': 'k1: v1', 'name': 'example_user'},
                      {'role': 'system', 'content': 'v1', 'name': 'example_assistant'},
                      {'role': 'system', 'content': 'k1: v2', 'name': 'example_user'},
                      {'role': 'system', 'content': 'v2', 'name': 'example_assistant'},
                      {'role': 'user', 'content': 'hello'},
                      {'role': 'user', 'content': 'hello2'},
                      {'role': 'user', 'content': 'k1: v'}], model='gpt-3.5-turbo')
        self.assertEqual(
            call_args, mock_openai_api.call_args_list[-1]
        )

        with self.assertRaises(ValueError):
            o = f(__extra_messages=[
                '',
                Message.user('hello2'),
            ])

    @mock.patch('openai.ChatCompletion.create')
    def test_return_obj(self, mock_openai_api):
        mock_openai_api.side_effect = gpt_text
        f = LmFunction.create(
            'do this',
            examples=[
                Example(input={"k1": 'v1'}, output='v1'),
                Example(input={"k1": 'v2'}, output='v2'),
            ],
            default_args={'k1': 'v'},
            gpt_opts=GptApiOptions(temperature=0.5)
        )

        o = f(__return_resp_obj=True)
        self.assertEqual(
            {'choices': [{'message': {'content': 'v0'}}]}
            , o)

        o = f(__override={'n': 3})
        self.assertEqual([
            'v0', 'v1', 'v2'
        ], o)
        o = f(__override={'n': 3}, __return_resp_obj=True)
        self.assertEqual(
            {'choices': [
                {'message': {'content': 'v0'}},
                {'message': {'content': 'v1'}},
                {'message': {'content': 'v2'}}
            ]
            }
            , o)
