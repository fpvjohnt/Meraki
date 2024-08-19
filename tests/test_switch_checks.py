import sys
import os
import unittest
from unittest.mock import AsyncMock, patch
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.checks.switch_checks import check_switch_ports, check_switch_stp  # Import your actual switch check functions
from src.api.meraki_api import MerakiAPI

class TestSwitchChecks(unittest.TestCase):
    def setUp(self):
        self.api = AsyncMock(spec=MerakiAPI)
        self.network_id = "test_network_id"
        self.switch_serial = "Q2XX-XXXX-XXXX"
        self.thresholds = {
            "port_utilization": 80,  # percent
            "stp_instances": 5
        }

    def asyncTest(func):
        def wrapper(*args, **kwargs):
            return asyncio.run(func(*args, **kwargs))
        return wrapper

    @asyncTest
    async def test_check_switch_ports(self):
        # Mock API response
        self.api.get_device_switch_ports_statuses.return_value = [
            {"portId": "1", "status": "Connected", "speed": "1 Gbps", "duplex": "full"},
            {"portId": "2", "status": "Disconnected"}
        ]

        result = await check_switch_ports(self.api, self.switch_serial, self.thresholds)

        self.assertTrue(result["is_ok"])
        self.assertEqual(result["connected_ports"], 1)

    @asyncTest
    async def test_check_switch_stp(self):
        # Mock API response
        self.api.get_network_switch_stp.return_value = {
            "instances": [
                {"id": "1", "rootBridge": {"address": "00:11:22:33:44:55"}},
                {"id": "2", "rootBridge": {"address": "00:11:22:33:44:66"}}
            ]
        }

        result = await check_switch_stp(self.api, self.network_id, self.thresholds)

        self.assertTrue(result["is_ok"])
        self.assertEqual(result["stp_instances"], 2)

if __name__ == '__main__':
    unittest.main()