import json
import unittest
from slambda import Example, TextFunctionMode, Definition, Message
from slambda.core import inspect_examples, NullaryFunction, create_function, UnaryFunction, KeywordFunction, \
    GptApiOptions


class TestExample(unittest.TestCase):
    def test_to_str_pair_empty_input(self):
        example = Example(output="Output String")
        definition = Definition()
        definition.default_message = "Default Message"
        expected_output = ("Default Message", "Output String")
        self.assertEqual(example.to_str_pair(definition), expected_output)

    def test_to_str_pair_str_input(self):
        example = Example(input="Input String", output="Output String")
        definition = Definition()
        expected_output = ("Input String", "Output String")
        self.assertEqual(example.to_str_pair(definition), expected_output)

    def test_to_str_pair_dict_input(self):
        input_dict = {"key1": "value1", "key2": "value2"}
        example = Example(input=input_dict, output="Output String")
        definition = Definition()
        expected_output = ("key1: value1\nkey2: value2", "Output String")
        self.assertEqual(example.to_str_pair(definition), expected_output)

    def test_to_str_pair_dict_input_with_template(self):
        input_dict = {"name": "jack", "age": 10}
        example = Example(input=input_dict, output="Output String")
        definition = Definition()
        definition.message_template = '{name} is {age} years old'
        expected_output = ("jack is 10 years old", "Output String")
        self.assertEqual(example.to_str_pair(definition), expected_output)

    def test_to_str_pair_str_output(self):
        example = Example(input="Input String", output="Output String")
        definition = Definition()
        expected_output = ("Input String", "Output String")
        self.assertEqual(example.to_str_pair(definition), expected_output)

    def test_to_str_pair_dict_output(self):
        output_dict = {"a": "10", "b": 20}
        example = Example(input="Input String", output=output_dict)
        definition = Definition()
        expected_output = ("Input String", json.dumps(output_dict))
        self.assertEqual(example.to_str_pair(definition), expected_output)

    def test_is_json_output_true(self):
        example = Example(output={"key": "value"})
        self.assertTrue(example.is_json_output)

    def test_is_json_output_false(self):
        example = Example(output="Output String")
        self.assertFalse(example.is_json_output)

    def test_is_str_output_true(self):
        example = Example(output="Output String")
        self.assertTrue(example.is_str_output)

    def test_is_str_output_false(self):
        example = Example(output={"key": "value"})
        self.assertFalse(example.is_str_output)

    def test_is_dict_input_true(self):
        example = Example(input={"key": "value"}, output="Output String")
        self.assertTrue(example.is_dict_input)

    def test_is_dict_input_false(self):
        example = Example(input="Input String", output="Output String")
        self.assertFalse(example.is_dict_input)

    def test_is_str_input_true(self):
        example = Example(input="Input String", output="Output String")
        self.assertTrue(example.is_str_input)

    def test_is_str_input_false(self):
        example = Example(input={"key": "value"}, output="Output String")
        self.assertFalse(example.is_str_input)

    def test_is_empty_input_true(self):
        example = Example(output="Output String")
        self.assertTrue(example.is_empty_input)

    def test_is_empty_input_false(self):
        example = Example(input="Input String", output="Output String")
        self.assertFalse(example.is_empty_input)

    def test_match_output_mode_json(self):
        example = Example(output={"key": "value"})
        self.assertTrue(example.match_output_mode(is_json=True))

    def test_match_output_mode_str(self):
        example = Example(output="Output String")
        self.assertTrue(example.match_output_mode(is_json=False))

    def test_match_call_mode_dict_input(self):
        example = Example(input={"key": "value"}, output="Output String")
        mode_list = [TextFunctionMode.KEYWORD]
        self.assertTrue(example.match_call_mode(mode_list))

    def test_match_call_mode_str_input(self):
        example = Example(input="Input String", output="Output String")
        mode_list = [TextFunctionMode.POS]
        self.assertTrue(example.match_call_mode(mode_list))

    def test_match_call_mode_false(self):
        example = Example(input="Input String", output="Output String")
        mode_list = []
        self.assertFalse(example.match_call_mode(mode_list))


class TestInspectExamples(unittest.TestCase):

    def test_json_output(self):
        example1 = Example(input="input1", output={'a': 1})
        example2 = Example(input='2', output={"key": "value"})
        examples = [example1, example2]

        mode_list = [TextFunctionMode.POS]
        self.assertTrue(inspect_examples(examples, mode_list, None))
        self.assertTrue(inspect_examples(examples, mode_list, True))
        with self.assertRaises(ValueError):
            inspect_examples(examples, mode_list, False)
        with self.assertRaises(ValueError):
            inspect_examples(examples, [], False)

    def test_str_output(self):
        example1 = Example(input="input1", output="a")
        example2 = Example(input='2', output='a')
        examples = [example1, example2]

        mode_list = [TextFunctionMode.POS]
        self.assertFalse(inspect_examples(examples, mode_list, None))
        self.assertFalse(inspect_examples(examples, mode_list, False))
        with self.assertRaises(ValueError):
            inspect_examples(examples, mode_list, True)

    def test_empty_input(self):
        example1 = Example(output="a")
        example2 = Example(output='a')
        examples = [example1, example2]

        inspect_examples(examples, [TextFunctionMode.NO_ARGS], None)
        inspect_examples(examples, [TextFunctionMode.POS, TextFunctionMode.NO_ARGS], None)
        inspect_examples(examples, [TextFunctionMode.KEYWORD, TextFunctionMode.NO_ARGS], None)

        with self.assertRaises(ValueError):
            inspect_examples(examples, [TextFunctionMode.KEYWORD], None)
        with self.assertRaises(ValueError):
            inspect_examples(examples, [TextFunctionMode.POS], None)

    def test_str_input(self):
        example1 = Example(input="input1", output="a")
        example2 = Example(input='2', output='a')
        examples = [example1, example2]

        inspect_examples(examples, [TextFunctionMode.POS], None)
        inspect_examples(examples, [TextFunctionMode.POS, TextFunctionMode.NO_ARGS], None)

        with self.assertRaises(ValueError):
            inspect_examples(examples, [TextFunctionMode.KEYWORD], None)
        with self.assertRaises(ValueError):
            inspect_examples(examples, [TextFunctionMode.NO_ARGS], None)

    def test_dict_input(self):
        example1 = Example(input={"a": 1}, output="a")
        example2 = Example(input={"a": 1}, output='a')
        examples = [example1, example2]

        inspect_examples(examples, [TextFunctionMode.KEYWORD], None)
        inspect_examples(examples, [TextFunctionMode.KEYWORD, TextFunctionMode.NO_ARGS], None)

        with self.assertRaises(ValueError):
            inspect_examples(examples, [TextFunctionMode.POS], None)
        with self.assertRaises(ValueError):
            inspect_examples(examples, [TextFunctionMode.NO_ARGS], None)

    def test_matching_modes(self):
        example1 = Example(input="input1", output="output1")
        example2 = Example(input={"key": "value"}, output={"key": "value"})

        examples = [example1, example2]
        mode_list = [TextFunctionMode.KEYWORD, TextFunctionMode.POS]
        json_output = False

        with self.assertRaises(ValueError):
            inspect_examples(examples, mode_list, json_output)

    def test_mismatched_modes(self):
        example1 = Example(input="input1", output="output1")

        examples = [example1]
        mode_list = [TextFunctionMode.KEYWORD]
        json_output = False

        with self.assertRaises(ValueError):
            inspect_examples(examples, mode_list, json_output)

    def test_matching_output_type(self):
        example1 = Example(input="input1", output="output1")
        example2 = Example(input="input2", output={"key": "value"})

        examples = [example1, example2]
        mode_list = [TextFunctionMode.KEYWORD, TextFunctionMode.POS]
        json_output = True

        with self.assertRaises(ValueError):
            inspect_examples(examples, mode_list, json_output)

    def test_mismatched_output_type(self):
        example1 = Example(input="input1", output={"key": "value"})
        example2 = Example(input="input2", output="output2")

        examples = [example1, example2]
        mode_list = [TextFunctionMode.KEYWORD, TextFunctionMode.POS]
        json_output = True

        with self.assertRaises(ValueError):
            inspect_examples(examples, mode_list, json_output)

    def test_mixed_output_type(self):
        example1 = Example(input="input1", output="output1")
        example2 = Example(input="input2", output={"key": "value"})
        example3 = Example(input="input3", output={"key": "value"})
        example4 = Example(input="input4", output="output4")

        examples = [example1, example2, example3, example4]
        mode_list = [TextFunctionMode.KEYWORD, TextFunctionMode.POS]
        json_output = None

        with self.assertRaises(ValueError):
            inspect_examples(examples, mode_list, json_output)


class TestNullaryFunction(unittest.TestCase):
    def test_by_instruction_and_examples(self):
        with self.assertRaises(ValueError):
            NullaryFunction()
        f = NullaryFunction.from_instruction(
            'do this',
            examples=[
                Example(output='hello')
            ]
        )

        f2 = create_function(
            'do this',
            examples=[
                Example(output='hello')
            ],
            allow_no_arg=True
        )

        self.assertEqual(f.definition, f2.definition)


class TestUnaryFunction(unittest.TestCase):
    def test_creation(self):
        with self.assertRaises(ValueError):
            UnaryFunction()

        f = UnaryFunction.from_instruction(
            'do this',
            examples=[
                Example(input='123', output='hello')
            ]
        )

        f2 = create_function(
            'do this',
            examples=[
                Example(input='123', output='hello')
            ],
            allow_pos=True
        )

        self.assertEqual(f.definition, f2.definition)


class TestKeywordFunction(unittest.TestCase):
    def test_creation(self):
        with self.assertRaises(ValueError):
            KeywordFunction()

        f = KeywordFunction.from_instruction(
            'do this',
            examples=[
                Example(input={'a': 1}, output='hello')
            ],

        )

        f2 = create_function(
            'do this',
            examples=[
                Example(input={'a': 1}, output='hello')],
            allow_keyword=True
        )

        self.assertEqual(f.definition, f2.definition)


class TestBasicInstructionFollowing(unittest.TestCase):

    def test_create_function(self):
        with self.assertRaises(ValueError) as context:
            create_function(
                'do this',
                allow_pos=True, allow_keyword=True
            )
        with self.assertRaises(ValueError) as context:
            create_function(
                'do this',
            )
        f = create_function(
            'do this',
            allow_keyword=True,
            message_template='{name} {age}'
        )
        self.assertEqual(['name', 'age'], f.definition.required_args)

    def test_create_function_with_gpt_opts(self):
        f = create_function(
            'do this',
            allow_pos=True,
            gpt_opts=GptApiOptions(temperature=2)
        )

        self.assertEqual(2, f.definition.gpt_opts.temperature)

    def test_create_nullary_function(self):
        pass

    def test_create_pos_function(self):
        pass

    def test_create_kw_function(self):
        pass

    def test_shortcut_constructor(self):
        self.assertEqual(
            Message.system(content='A system message'),
            Message(role='system', content='A system message')
        )

        self.assertEqual(
            Message.user(content='A user message'),
            Message(role='user', content='A user message')
        )

        self.assertEqual(
            Message.assistant(content='A assistant message'),
            Message(role='assistant', content='A assistant message')
        )

        self.assertEqual(
            Message.example_user(content='A system message'),
            Message(role='system', content='A system message', name='example_user')
        )

        self.assertEqual(
            Message.example_assistant(content='A system message'),
            Message(role='system', content='A system message', name='example_assistant')
        )

    def test_follow_instruction(self):
        self.maxDiff = None
        t = Definition(
            init_messages=[
                Message.system('A system message')
            ],
            default_message='this receive no arg'
        )

        self.assertListEqual(
            [Message(role='system', content='A system message')],
            t.init_messages
        )

        t.from_instruction(
            'this is a instruction'
        )

        self.assertListEqual(
            [Message(role='system', content='this is a instruction')],
            t.init_messages
        )

        examples = [
            Example(f"i-{i}", f"o-{i}") for i in range(2)
        ]

        t.from_instruction(
            'this is the 2nd instruction', examples
        )

        self.assertListEqual(
            [
                Message(role='system', content='this is the 2nd instruction'),
                Message(role='system', content='i-0', name='example_user'),
                Message(role='system', content='o-0', name='example_assistant'),
                Message(role='system', content='i-1', name='example_user'),
                Message(role='system', content='o-1', name='example_assistant'),
            ],
            t.init_messages
        )


if __name__ == '__main__':
    unittest.main()
