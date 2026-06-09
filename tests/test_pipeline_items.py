import unittest

from pipeline_items import parse_model_items


class PipelineItemsTest(unittest.TestCase):
    def test_parse_model_items_accepts_json_array_inside_text(self):
        raw = '结果如下：[{"类型":"发票","发票号码":"INV-1"}]'

        self.assertEqual(parse_model_items(raw), [{"类型": "发票", "发票号码": "INV-1"}])

    def test_parse_model_items_accepts_single_object_fallback(self):
        raw = '{"类型":"银行回单","回单编号":"B-1"}'

        self.assertEqual(parse_model_items(raw), [{"类型": "银行回单", "回单编号": "B-1"}])

    def test_parse_model_items_returns_empty_list_for_invalid_json(self):
        self.assertEqual(parse_model_items("不是 JSON"), [])


if __name__ == "__main__":
    unittest.main()
