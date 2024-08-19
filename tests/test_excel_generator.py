import unittest
import os
from src.utils.excel_generator import generate_excel_report

class TestExcelGenerator(unittest.TestCase):
    def test_generate_excel_report(self):
        test_results = {
            "Network1": {
                "check1": {"is_ok": True},
                "check2": {"is_ok": False, "issues": [{"message": "Test issue"}]}
            },
            "Network2": {
                "check1": {"is_ok": False, "message": "Test message"}
            }
        }
        org_name = "Test Org"
        generate_excel_report(test_results, org_name)
        filename = f"{org_name}_health_check_report.xlsx"
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)  # Clean up

if __name__ == '__main__':
    unittest.main()