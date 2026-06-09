import unittest

from match_and_export import (
    amounts_match,
    build_fake_reasons,
    clean_amount,
    dedupe_invoices,
    drop_blank_documents,
    expense_category,
    has_amount_match,
    is_foreign_bank,
    is_foreign_inv,
    match_items,
    parse_expected_voucher_no,
    split_items_by_type,
)


class MatchAndExportHelpersTest(unittest.TestCase):
    def test_clean_amount_handles_currency_and_invalid_values(self):
        self.assertEqual(clean_amount("￥1,234.567"), 1234.57)
        self.assertEqual(clean_amount("USD 88.1"), 88.1)
        self.assertIsNone(clean_amount("not-a-number"))

    def test_amounts_match_uses_absolute_or_relative_tolerance(self):
        self.assertTrue(amounts_match(100.0, 100.4))
        self.assertTrue(amounts_match(10000.0, 10050.0))
        self.assertFalse(amounts_match(100.0, 103.0))
        self.assertFalse(amounts_match(0, 0))

    def test_parse_expected_voucher_no_from_category_filename(self):
        self.assertEqual(parse_expected_voucher_no("24060123销"), "123")
        self.assertEqual(parse_expected_voucher_no("240600123管特"), "123")
        self.assertEqual(parse_expected_voucher_no("plain-name"), "")

    def test_has_amount_match_checks_invoices_and_banks_independently(self):
        voucher = {"_金额": 200.0}
        invoices = [{"_价税合计": 200.0}]
        banks = []
        self.assertTrue(has_amount_match(voucher, invoices, banks))

        invoices = []
        banks = [{"_交易金额": 200.0}]
        self.assertTrue(has_amount_match(voucher, invoices, banks))

    def test_foreign_document_detection(self):
        self.assertTrue(is_foreign_inv({"销售方名称": "Example Limited"}))
        self.assertTrue(is_foreign_inv({"发票号码": "INV-001"}))
        self.assertFalse(is_foreign_inv({"销售方名称": "北京供应商", "发票号码": "123456"}))
        self.assertTrue(is_foreign_bank({"交易金额": "USD 120.00"}))
        self.assertFalse(is_foreign_bank({"交易金额": "120.00"}))

    def test_document_cleanup_helpers(self):
        items = [
            {"type": "记账凭证"},
            {"type": "发票", "发票号码": "A"},
            {"type": "银行回单", "回单编号": "B"},
        ]
        vouchers, invoices, banks = split_items_by_type(items)
        self.assertEqual(len(vouchers), 1)
        self.assertEqual(len(invoices), 1)
        self.assertEqual(len(banks), 1)

        invoices, banks = drop_blank_documents(
            [{"发票号码": "", "价税合计": ""}, {"发票号码": "A", "价税合计": ""}],
            [{"回单编号": "", "交易金额": ""}, {"回单编号": "", "交易金额": "10"}],
        )
        self.assertEqual(len(invoices), 1)
        self.assertEqual(len(banks), 1)

        self.assertEqual(len(dedupe_invoices([{"发票号码": "A"}, {"发票号码": "A"}])), 1)

    def test_fake_reasons_and_expense_category(self):
        reasons = build_fake_reasons([{"凭证编号": "999", "page": 5}], boundary=3, expected_vno="123")
        self.assertEqual(reasons, ["999(页码异常)"])
        self.assertEqual(expense_category("24060123销"), "销售费用")
        self.assertEqual(expense_category("24060123研"), "研发费用")
        self.assertEqual(expense_category("24060123管"), "管理费用")
        self.assertEqual(expense_category("24060123其他"), "")

    def test_match_items_complete_amount_match(self):
        matched = match_items(
            [
                _voucher("24060123销", page=1, amount="100.00", number="123"),
                _invoice("24060123销", page=2, amount="100.00", number="INV-1"),
                _bank("24060123销", page=3, amount="100.00", number="BANK-1"),
            ]
        )

        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["voucher"]["凭证编号"], "123")
        self.assertEqual(matched[0]["invoice"]["发票号码"], "INV-1")
        self.assertEqual(matched[0]["bank"]["回单编号"], "BANK-1")

    def test_match_items_filters_late_fake_voucher(self):
        matched = match_items(
            [
                _voucher("24060123销", page=1, amount="100.00", number="123"),
                _invoice("24060123销", page=2, amount="100.00", number="INV-1"),
                _bank("24060123销", page=3, amount="100.00", number="BANK-1"),
                _voucher("24060123销", page=4, amount="100.00", number="999"),
            ]
        )

        self.assertEqual(len(matched), 1)
        self.assertIn("999(页码异常)", matched[0]["fake_reasons"])


def _voucher(pdf_name, page, amount, number="123"):
    return {
        "pdf_name": pdf_name,
        "page": page,
        "type": "记账凭证",
        "凭证编号": number,
        "记账日期": "2024-06-01",
        "公司名称": "测试公司",
        "摘要": "测试",
        "金额": amount,
        "_金额": clean_amount(amount),
    }


def _invoice(pdf_name, page, amount, number="INV-1"):
    return {
        "pdf_name": pdf_name,
        "page": page,
        "type": "发票",
        "发票号码": number,
        "开票日期": "2024-06-01",
        "销售方名称": "测试供应商",
        "价税合计": amount,
        "_价税合计": clean_amount(amount),
    }


def _bank(pdf_name, page, amount, number="BANK-1"):
    return {
        "pdf_name": pdf_name,
        "page": page,
        "type": "银行回单",
        "回单编号": number,
        "交易日期": "2024-06-01",
        "交易金额": amount,
        "_交易金额": clean_amount(amount),
    }


if __name__ == "__main__":
    unittest.main()
