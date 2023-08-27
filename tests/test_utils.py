import unittest

from slambda.utils import extract_required_keywords, try_parse_json
from slambda.core import InputCounter, OutputCounter, FunctionOutputConfig, FunctionInputConfig


class TestUtils(unittest.TestCase):
    def test_extract_required_keywords(self):
        ns = extract_required_keywords('{name} is {age} years old.')
        self.assertListEqual(['name', 'age'], ns)

    def test_try_parse_json(self):
        d, parsed = try_parse_json('{"k": 0}')
        self.assertDictEqual({"k": 0}, d)
        self.assertTrue(parsed)

    def test_try_parse_not_json(self):
        d, parsed = try_parse_json('{"k": 0')
        self.assertEqual('{"k": 0', d)
        self.assertFalse(parsed)

    def test_input_counter(self):
        counter = InputCounter()

        self.assertEqual(False, counter.has_none)
        self.assertEqual(False, counter.has_keyword)
        self.assertEqual(False, counter.has_positional)

        counter.count(None)
        self.assertEqual(True, counter.has_none)
        self.assertEqual(False, counter.has_keyword)
        self.assertEqual(False, counter.has_positional)

        counter.count('None')
        counter.count('1')
        self.assertEqual(True, counter.has_none)
        self.assertEqual(False, counter.has_keyword)
        self.assertEqual(True, counter.has_positional)

        counter.count({'a': None})
        counter.count({'a': 1})
        counter.count({'a': 2})
        self.assertEqual(True, counter.has_none)
        self.assertEqual(True, counter.has_keyword)
        self.assertEqual(True, counter.has_positional)

        self.assertEqual(1, counter.NONE)
        self.assertEqual(2, counter.POS)
        self.assertEqual(3, counter.KEYWORD)

        with self.assertRaises(ValueError):
            counter.count(1)

        counter2 = InputCounter()
        self.assertEqual(False, counter2.has_none)
        self.assertEqual(False, counter2.has_keyword)
        self.assertEqual(False, counter2.has_positional)
        self.assertEqual(True, counter.has_none)
        self.assertEqual(True, counter.has_keyword)
        self.assertEqual(True, counter.has_positional)

    def test_input_counter_to_cfg_invalid(self):
        with self.assertRaises(ValueError):
            # no default
            nothing = (0, 0, 0)
            cfg = InputCounter(*nothing).to_config()
        with self.assertRaises(ValueError):
            kw_and_pos = (1, 1, 0)
            cfg = InputCounter(*kw_and_pos).to_config()
        with self.assertRaises(ValueError):
            everything = (1, 1, 1)
            cfg = InputCounter(*everything).to_config()

    def test_input_counter_to_cfg_none_only(self):
        none_only = (0, 0, 1)
        with self.assertRaises(ValueError):
            # no default
            cfg = InputCounter(*none_only).to_config()

        with self.assertRaises(ValueError):
            cfg = InputCounter(*none_only).to_config(default_args='', strict_no_args=True)

        with self.assertRaises(ValueError):
            cfg = InputCounter(*none_only).to_config(default_args={}, strict_no_args=True)

        with self.assertRaises(ValueError):
            cfg = InputCounter(*none_only).to_config(default_args='', strict_no_args=False)

        with self.assertRaises(ValueError):
            cfg = InputCounter(*none_only).to_config(default_args={}, strict_no_args=False)

        cfg = InputCounter(*none_only).to_config(default_args='1', strict_no_args=True)
        self.assertEqual(FunctionInputConfig.nullary_pos(), cfg)

        cfg = InputCounter(*none_only).to_config(default_args={'a': 1}, strict_no_args=True)
        self.assertEqual(FunctionInputConfig.nullary_keyword(), cfg)

        cfg = InputCounter(*none_only).to_config(default_args='a', strict_no_args=False)
        self.assertEqual(FunctionInputConfig.unary(True), cfg)

        cfg = InputCounter(*none_only).to_config(default_args={'a': 1}, strict_no_args=False)
        self.assertEqual(FunctionInputConfig.keyword(True), cfg)

    def test_input_counter_to_cfg_keyword(self):
        kw_only = (1, 0, 0)

        cfg = InputCounter(*kw_only).to_config()
        self.assertEqual(FunctionInputConfig.keyword(False), cfg)

        cfg = InputCounter(*kw_only).to_config(default_args='')
        self.assertEqual(FunctionInputConfig.keyword(False), cfg)

        cfg = InputCounter(*kw_only).to_config(default_args='1')
        self.assertEqual(FunctionInputConfig.keyword(False), cfg)

        cfg = InputCounter(*kw_only).to_config(default_args={})
        self.assertEqual(FunctionInputConfig.keyword(False), cfg)

        cfg = InputCounter(*kw_only).to_config(default_args={'a': 1})
        self.assertEqual(FunctionInputConfig.keyword(True), cfg)

    def test_input_counter_to_cfg_keyword_and_none(self):
        kw_and_none = (1, 0, 1)
        with self.assertRaises(ValueError):
            cfg = InputCounter(*kw_and_none).to_config()

        with self.assertRaises(ValueError):
            cfg = InputCounter(*kw_and_none).to_config(default_args='')

        with self.assertRaises(ValueError):
            cfg = InputCounter(*kw_and_none).to_config(default_args={})

        with self.assertRaises(ValueError):
            cfg = InputCounter(*kw_and_none).to_config(default_args='1')
        cfg = InputCounter(*kw_and_none).to_config(default_args={'a': 1})
        self.assertEqual(FunctionInputConfig.keyword(True), cfg)

    def test_input_counter_to_cfg_pos(self):
        pos_only = (0, 1, 0)

        cfg = InputCounter(*pos_only).to_config()
        self.assertEqual(FunctionInputConfig.unary(False), cfg)

        cfg = InputCounter(*pos_only).to_config(default_args='')
        self.assertEqual(FunctionInputConfig.unary(False), cfg)

        cfg = InputCounter(*pos_only).to_config(default_args='1')
        self.assertEqual(FunctionInputConfig.unary(True), cfg)

        cfg = InputCounter(*pos_only).to_config(default_args={})
        self.assertEqual(FunctionInputConfig.unary(False), cfg)

        cfg = InputCounter(*pos_only).to_config(default_args={'a': 1})
        self.assertEqual(FunctionInputConfig.unary(False), cfg)

    def test_input_counter_to_cfg_pos_and_none(self):
        pos_and_none = (0, 1, 1)
        with self.assertRaises(ValueError):
            cfg = InputCounter(*pos_and_none).to_config()

        with self.assertRaises(ValueError):
            cfg = InputCounter(*pos_and_none).to_config(default_args='')

        with self.assertRaises(ValueError):
            cfg = InputCounter(*pos_and_none).to_config(default_args={})
        with self.assertRaises(ValueError):
            cfg = InputCounter(*pos_and_none).to_config(default_args={'a': 1})

        cfg = InputCounter(*pos_and_none).to_config(default_args='1')
        self.assertEqual(FunctionInputConfig.unary(True), cfg)

    def test_output_counter(self):
        counter = OutputCounter()
        counter.count('1')

        self.assertEqual(True, counter.has_str)
        self.assertEqual(False, counter.has_json)

        counter.count({'a': None})
        counter.count({'a': 1})
        counter.count({'a': 2})
        self.assertEqual(True, counter.has_str)
        self.assertEqual(True, counter.has_json)

        self.assertEqual(1, counter.str_count)
        self.assertEqual(3, counter.json_count)

        with self.assertRaises(ValueError):
            counter.count(None)
        with self.assertRaises(ValueError):
            counter.count(1)

        counter2 = OutputCounter()
        self.assertEqual(False, counter2.has_str)
        self.assertEqual(False, counter2.has_json)
        self.assertEqual(True, counter.has_str)
        self.assertEqual(True, counter.has_json)

    def test_output_counter_to_cfg(self):
        with self.assertRaises(ValueError):
            OutputCounter(2, 2).to_config()

        cfg = OutputCounter(2, 0).to_config()
        self.assertEqual(FunctionOutputConfig(cast_to_json=False), cfg)

        cfg = OutputCounter(0, 2).to_config()
        self.assertEqual(FunctionOutputConfig(cast_to_json=True), cfg)
        with self.assertRaises(ValueError):
            OutputCounter(0, 0).to_config()


if __name__ == '__main__':
    unittest.main()
