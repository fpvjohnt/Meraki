import pytest
from unittest.mock import AsyncMock
from src.checks.organization_checks import check_organization_admins, check_organization_inventory
from src.api.meraki_api import MerakiAPI

class TestOrganizationChecks:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.api = AsyncMock(spec=MerakiAPI)
        self.org_id = "test_org_id"
        self.thresholds = {
            'max_admins': 10,
            'max_full_admins': 5,
            'inactive_admin_days': 30,
            'inventory_utilization': 80,
            'max_unclaimed_devices': 5,
            'min_firmware_version': '1.0'
        }

    @pytest.mark.asyncio
    async def test_check_organization_admins(self):
        self.api.get_organization_admins.return_value = [
            {"orgAccess": "full", "lastActive": "2023-01-01T00:00:00Z"} for _ in range(6)
        ]
        result = await check_organization_admins(self.api, self.org_id, self.thresholds)
        assert result["is_ok"] == False
        assert len(result["issues"]) > 0

    @pytest.mark.asyncio
    async def test_check_organization_inventory(self):
        self.api.get_organization_inventory_devices.return_value = [
            {"networkId": "net1"} for _ in range(90)
        ] + [{"networkId": None} for _ in range(10)]
        result = await check_organization_inventory(self.api, self.org_id, self.thresholds)
        assert result["is_ok"] == False
        assert len(result["issues"]) > 0