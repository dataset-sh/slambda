from unittest import TestCase

from slambda import Definition, Example
from slambda.core import FunctionInputConfig, FunctionInputType, FunctionOutputConfig, LmOutputCastingError


class TestExample(TestCase):
    def test_create_example(self):
        self.assertEqual(Example('1', '2'), Example(input='1', output='2'))

    def test_example_input_type(self):
        self.assertEqual(Example('1', '2').input_type, FunctionInputType.UNARY)
        self.assertEqual(Example({'1': 1}, '2').input_type, FunctionInputType.KEYWORD)
        self.assertEqual(Example(output='2').input_type, None)

    def test_keyword_input_no_template(self):
        input_config = FunctionInputConfig.keyword(False)
        input_arg = {"param1": "value1", "param2": "value2"}
        required_args = ["param1", "param2"]

        result = Definition.render_input(input_config, input_arg, None, required_args, None)
        expected_result = "param1: value1\nparam2: value2"
        self.assertEqual(result, expected_result)

    def test_keyword_input_template(self):
        input_config = FunctionInputConfig.keyword(False)
        input_arg = {"param1": "value1", "param2": "value2"}
        required_args = ["param1", "param2"]
        message_template = "Params: {param1}, {param2}"

        result = Definition.render_input(input_config, input_arg, None, required_args, message_template)
        self.assertEqual(result, "Params: value1, value2")

    def test_keyword_input_missing_required_arg(self):
        input_config = FunctionInputConfig.keyword(False)
        input_arg = {"param1": "value1"}
        required_args = ["param1", "param2"]
        message_template = "Params: {param1}, {param2}"

        with self.assertRaises(ValueError):
            Definition.render_input(input_config, input_arg, None, required_args, message_template)

    def test_keyword_input_allow_none(self):
        input_config = FunctionInputConfig(input_type=FunctionInputType.KEYWORD, allow_none=True)
        input_arg = None
        default_args = {"param1": "default_value1", "param2": "default_value2"}
        required_args = ["param1", "param2"]
        message_template = "Params: {param1}, {param2}"

        result = Definition.render_input(input_config, input_arg, default_args, required_args, message_template)
        self.assertEqual(result, "Params: default_value1, default_value2")
        with self.assertRaises(ValueError):
            result = Definition.render_input(input_config, input_arg, None, None, None)
        with self.assertRaises(ValueError):
            result = Definition.render_input(input_config, input_arg, '', None, None)

        with self.assertRaises(ValueError):
            result = Definition.render_input(input_config, input_arg, 12, None, None)

    def test_unary_input_allow_none(self):
        input_config = FunctionInputConfig(input_type=FunctionInputType.UNARY, allow_none=True)
        input_arg = None
        default_arg = "default_value"

        result = Definition.render_input(input_config, input_arg, default_arg, None, None)
        self.assertEqual(result, "default_value")

        with self.assertRaises(ValueError):
            result = Definition.render_input(input_config, input_arg, {}, None, None)

        with self.assertRaises(ValueError):
            result = Definition.render_input(input_config, input_arg, None, None, None)

    def test_unary_input_normal(self):
        input_config = FunctionInputConfig.unary(False)
        input_arg = "single_value"
        default_arg = "default_value"

        result = Definition.render_input(input_config, input_arg, default_arg, None, None)
        self.assertEqual(result, "single_value")

    def test_unary_input_invalid(self):
        input_config = FunctionInputConfig.unary(False)
        input_arg = {"param": "value"}

        with self.assertRaises(ValueError):
            Definition.render_input(input_config, input_arg, None, None, None)

        with self.assertRaises(ValueError):
            Definition.render_input(input_config, input_arg, "", None, None)

    def test_nullary_input_with_default(self):
        input_config = FunctionInputConfig.nullary_pos()
        default_args = "default_value"

        result = Definition.render_input(input_config, None, default_args, None, None)
        self.assertEqual(result, "default_value")

    def test_nullary_input_without_default(self):
        input_config = FunctionInputConfig.nullary_pos()

        with self.assertRaises(ValueError):
            Definition.render_input(input_config, None, None, None, None)

    #
    def test_render_output(self):
        with self.assertRaises(ValueError) as ctx:
            v = Definition.render_output_example(
                FunctionOutputConfig(cast_to_json=True),
                ''
            )

        v = Definition.render_output_example(
            FunctionOutputConfig(cast_to_json=True),
            [{"a": 1}]
        )
        self.assertEqual('[{"a": 1}]', v)

        v = Definition.render_output_example(
            FunctionOutputConfig(cast_to_json=True),
            {"a": 1}
        )
        self.assertEqual('{"a": 1}', v)

        v = Definition.render_output_example(
            FunctionOutputConfig(cast_to_json=False),
            'aaa'
        )

        self.assertEqual('aaa', v)

        with self.assertRaises(ValueError) as ctx:
            v = Definition.render_output_example(
                FunctionOutputConfig(cast_to_json=False),
                {"a": 1}
            )
        with self.assertRaises(ValueError) as ctx:
            v = Definition.render_output_example(
                FunctionOutputConfig(cast_to_json=False),
                [{"a": 1}]
            )

    def test_cast_llm_output(self):
        v = Definition.cast_lm_output(
            FunctionOutputConfig(cast_to_json=False),
            "{"
        )
        self.assertEqual('{', v)

        v = Definition.cast_lm_output(
            FunctionOutputConfig(cast_to_json=False),
            "{}"
        )
        self.assertEqual('{}', v)

        with self.assertRaises(LmOutputCastingError) as ctx:
            v = Definition.cast_lm_output(
                FunctionOutputConfig(cast_to_json=True),
                "{"
            )
        self.assertEqual('{', ctx.exception.llm_output)

        v = Definition.cast_lm_output(
            FunctionOutputConfig(cast_to_json=True),
            '{"a": 1}'
        )

        self.assertDictEqual({"a": 1}, v)


class TestExamples(TestCase):
    def test_detect_input_output_type_empty_input(self):
        # Create example instances
        examples = [

        ]
        with self.assertRaises(ValueError):
            input_config, output_config = Definition.detect_input_output_type(examples)

    def test_detect_input_output_type_mix_input(self):
        # Create example instances
        examples = [
            Example(input={'a': 10}, output={'result': 20}),
            Example(input='test', output='output'),
            Example(input=None, output=['list', 'of', 'items']),
        ]
        with self.assertRaises(ValueError):
            input_config, output_config = Definition.detect_input_output_type(examples)

        examples = [
            Example(input={'a': 10}, output={'result': 20}),
            Example(input='test', output='output'),
        ]
        with self.assertRaises(ValueError):
            input_config, output_config = Definition.detect_input_output_type(examples)

    def test_detect_input_output_type_mix_output(self):
        # Create example instances
        examples = [
            Example(input={'a': 10}, output={'result': 20}),
            Example(input={'a': 10}, output='output'),
        ]
        with self.assertRaises(ValueError):
            input_config, output_config = Definition.detect_input_output_type(examples)

        examples = [
            Example(input={'a': 10}, output={'result': 20}),
            Example(input={'a': 10}, output='output'),
        ]
        with self.assertRaises(ValueError):
            input_config, output_config = Definition.detect_input_output_type(examples)

    def test_detect_input_output_type_invalid_input_none(self):
        # Create example instances
        examples = [
            Example(output="{'result': 20}"),
            Example(input={'a': 10}, output='output'),
        ]
        with self.assertRaises(ValueError):
            input_config, output_config = Definition.detect_input_output_type(examples)
        examples = [
            Example(output="{'result': 20}"),
            Example(input='', output='output'),
        ]
        with self.assertRaises(ValueError):
            input_config, output_config = Definition.detect_input_output_type(examples)

    def test_detect_input_str(self):
        # Create example instances
        examples = [
            Example(output='asdf'),
            Example(input="{'a': 10}", output='output'),
        ]
        input_config, output_config = Definition.detect_input_output_type(examples, default_args='a')
        self.assertEqual(FunctionInputConfig.unary(True), input_config)
        self.assertEqual(FunctionOutputConfig(cast_to_json=False, cast_or_fail=True), output_config)

        examples = [
            Example(input="{'a': 10}", output='outpu2t'),
            Example(input='', output='output'),
        ]
        input_config, output_config = Definition.detect_input_output_type(examples, default_args='a')
        self.assertEqual(FunctionInputConfig.unary(True), input_config)
        self.assertEqual(FunctionOutputConfig(cast_to_json=False, cast_or_fail=True), output_config)

        examples = [
            Example(input="{'a': 10}", output='outpu2t'),
            Example(input='', output='output'),
        ]
        input_config, output_config = Definition.detect_input_output_type(examples, default_args='a')
        self.assertEqual(FunctionInputConfig.unary(True), input_config)
        self.assertEqual(FunctionOutputConfig(cast_to_json=False, cast_or_fail=True), output_config)

    def test_detect_input_kw(self):
        # Create example instances
        examples = [
            Example(input={'a': 10}, output='outpu2t'),
            Example(input={}, output='output'),
            Example(input=None, output='output'),
        ]

        input_config, output_config = Definition.detect_input_output_type(examples, default_args={'v': 1})
        self.assertEqual(FunctionInputConfig.keyword(True), input_config)
        self.assertEqual(FunctionOutputConfig(cast_to_json=False, cast_or_fail=True), output_config)

        examples = []

        with self.assertRaises(ValueError):
            input_config, output_config = Definition.detect_input_output_type(examples)

    def test_missing_allow_none(self):
        # Create example instances
        examples = [
            Example(input={'a': 10}, output='outpu2t'),
            Example(input=None, output='output'),
        ]
        input_config, output_config = Definition.detect_input_output_type(examples, default_args={'a': 1})
        self.assertEqual(FunctionInputConfig.keyword(True), input_config)
        self.assertEqual(FunctionOutputConfig(cast_to_json=False), output_config)

        examples = [
            Example(input={'a': 10}, output='outpu2t'),
            Example(input={'a': 10}, output='output'),
        ]

        input_config, output_config = Definition.detect_input_output_type(examples, default_args={'a': 1})
        self.assertEqual(FunctionInputConfig.keyword(True), input_config)
        self.assertEqual(FunctionOutputConfig(cast_to_json=False), output_config)

    def test_nullary(self):
        # Create example instances

        examples = [
            Example(output='outpu2t'),
            Example(output='output'),
        ]

        input_config, output_config = Definition.detect_input_output_type(examples, default_args='a')
        self.assertEqual(FunctionInputConfig.unary(True), input_config)
        self.assertEqual(FunctionOutputConfig(cast_to_json=False), output_config)

        input_config, output_config = Definition.detect_input_output_type(examples, default_args={'a': 1})
        self.assertEqual(FunctionInputConfig.keyword(True), input_config)
        self.assertEqual(FunctionOutputConfig(cast_to_json=False), output_config)

        input_config, output_config = Definition.detect_input_output_type(examples, default_args='a',
                                                                          strict_no_args=True)
        self.assertEqual(FunctionInputConfig.nullary_pos(), input_config)
        self.assertEqual(FunctionOutputConfig(cast_to_json=False), output_config)

        input_config, output_config = Definition.detect_input_output_type(examples, default_args={'a': 1},
                                                                          strict_no_args=True)
        self.assertEqual(FunctionInputConfig.nullary_keyword(), input_config)
        self.assertEqual(FunctionOutputConfig(cast_to_json=False), output_config)
