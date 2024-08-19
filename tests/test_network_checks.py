import pytest
from unittest.mock import AsyncMock
from src.checks.network_checks import check_network_firmware
from src.api.meraki_api import MerakiAPI

class TestNetworkChecks:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.api = AsyncMock(spec=MerakiAPI)
        self.api.get_network_firmware_upgrades = AsyncMock()
        self.network_id = "test_network_id"
        self.thresholds = {
            "health_score": 80,
            "firmware_age": 90
        }

    @pytest.mark.asyncio
    async def test_check_network_firmware(self):
        self.api.get_network_firmware_upgrades.return_value = {
            "currentVersion": {"firmware": "old"},
            "lastUpgrade": {
                "toVersion": {"firmware": "new"},
                "releaseDate": "2023-01-01T00:00:00Z"
            }
        }
        result = await check_network_firmware(self.api, self.network_id, self.thresholds)
        assert result["is_ok"] == False
        assert len(result["issues"]) == 1