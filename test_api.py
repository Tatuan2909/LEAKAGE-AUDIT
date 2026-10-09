"""Kiểm thử API và ứng dụng web (test_api.py)."""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import unittest
from app.app import app


class TestProject19API(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_endpoint(self):
        """Kiểm tra GET /api/health."""
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertTrue(data['honest_model_loaded'])

    def test_metrics_endpoint(self):
        """Kiểm tra GET /api/metrics."""
        res = self.client.get('/api/metrics')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('experiment_results', data)
        self.assertIn('experiment_2_leakage_audit', data['experiment_results'])

    def test_score_honest_valid(self):
        """Kiểm tra POST /api/session-score với dữ liệu hợp lệ (Honest Model)."""
        payload = {
            "Administrative": 3,
            "Administrative_Duration": 80.0,
            "Informational": 1,
            "Informational_Duration": 25.0,
            "ProductRelated": 30,
            "ProductRelated_Duration": 1500.0,
            "BounceRates": 0.005,
            "ExitRates": 0.02,
            "SpecialDay": 0.0,
            "Month": "Nov",
            "OperatingSystems": 2,
            "Browser": 2,
            "Region": 1,
            "TrafficType": 2,
            "VisitorType": "Returning_Visitor",
            "Weekend": False
        }
        res = self.client.post('/api/session-score', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('purchase_probability', data['prediction'])
        self.assertFalse(data['model_audit_info']['page_values_used'])
        self.assertNotIn('leakage_comparison', data)

    def test_score_leakage_audit(self):
        """Kiểm tra khi client gửi kèm PageValues thì API phát hiện và đối chiếu rò rỉ."""
        payload = {
            "Administrative": 3,
            "Administrative_Duration": 80.0,
            "Informational": 1,
            "Informational_Duration": 25.0,
            "ProductRelated": 30,
            "ProductRelated_Duration": 1500.0,
            "BounceRates": 0.005,
            "ExitRates": 0.02,
            "SpecialDay": 0.0,
            "Month": "Nov",
            "OperatingSystems": 2,
            "Browser": 2,
            "Region": 1,
            "TrafficType": 2,
            "VisitorType": "Returning_Visitor",
            "Weekend": False,
            "PageValues": 45.0
        }
        res = self.client.post('/api/session-score', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('leakage_comparison', data)
        self.assertGreater(data['leakage_comparison']['naive_probability'], data['prediction']['purchase_probability'])
        print(f"[TEST LEAKAGE] Honest Prob: {data['prediction']['purchase_probability']} | Naive Prob (+PageValues): {data['leakage_comparison']['naive_probability']}")

    def test_validation_missing_fields(self):
        """Kiểm tra bắt lỗi khi thiếu trường bắt buộc."""
        bad_payload = {"Administrative": 2}
        res = self.client.post('/api/session-score', json=bad_payload)
        self.assertEqual(res.status_code, 422)
        data = res.get_json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('errors', data)


if __name__ == '__main__':
    unittest.main()
