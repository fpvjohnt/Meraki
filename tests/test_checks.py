import pytest
from unittest.mock import AsyncMock, patch
from src.checks import network_checks, organization_checks, switch_checks, wireless_checks
from src.api.meraki_api import MerakiAPI

@pytest.fixture
def mock_api():
    api = AsyncMock(spec=MerakiAPI)
    api.get_network_firmware_upgrades = AsyncMock()
    api.get_organization_admins = AsyncMock()
    api.get_organization_inventory_devices = AsyncMock()
    api.get_device_switch_ports_statuses = AsyncMock()
    api.get_network_switch_stp = AsyncMock()
    return api

@pytest.fixture
def thresholds():
    return {
        'max_admins': 10,
        'max_full_admins': 5,
        'inactive_admin_days': 30,
        'inventory_utilization': 80,
        'max_unclaimed_devices': 5,
        'min_firmware_version': '1.0',
        'stp_instances': 5,
        'port_utilization': 80,
        'ssid_amount': 4,
        '5G Channel Utilization': 50,
        '5G Occurances Warning': 2,
        '5G Occurances Alarm': 4,
        '5G Min TX Power': 10,
        '5G Min Bitrate': 12,
        '5G Max Channel Width': 40
    }

@pytest.mark.asyncio
async def test_check_network_firmware(mock_api, thresholds):
    mock_api.get_network_firmware_upgrades.return_value = {
        "currentVersion": {"firmware": "old"},
        "lastUpgrade": {
            "toVersion": {"firmware": "new"},
            "releaseDate": "2023-01-01T00:00:00Z"
        }
    }
    result = await network_checks.check_network_firmware(mock_api, "test_network_id", thresholds)
    assert result["is_ok"] == False
    assert len(result["issues"]) == 1

@pytest.mark.asyncio
async def test_check_organization_admins(mock_api, thresholds):
    mock_api.get_organization_admins.return_value = [
        {"orgAccess": "full", "lastActive": "2023-01-01T00:00:00Z"} for _ in range(6)
    ]
    result = await organization_checks.check_organization_admins(mock_api, "org_id", thresholds)
    assert result["is_ok"] == False
    assert len(result["issues"]) > 0

@pytest.mark.asyncio
async def test_check_switch_ports(mock_api, thresholds):
    mock_api.get_device_switch_ports_statuses.return_value = [
        {"status": "Connected", "speed": "100 Mbps", "duplex": "full", "portId": "1"}
    ]
    result = await switch_checks.check_switch_ports(mock_api, "switch_serial", thresholds)
    assert result['is_ok'] == True
    assert result['connected_ports'] == 1

@pytest.mark.asyncio
async def test_check_switch_stp(mock_api, thresholds):
    mock_api.get_network_switch_stp.return_value = {
        "stpInstances": [
            {"rootBridge": {"address": "00:11:22:33:44:55"}, "stpMode": "rstp"},
            {"rootBridge": {"address": "AA:BB:CC:DD:EE:FF"}, "stpMode": "rstp"}
        ],
        "topologyChanges": 15
    }
    result = await switch_checks.check_switch_stp(mock_api, "network_id", thresholds)
    assert result['is_ok'] == False
    assert len(result['issues']) > 0
    assert result['stp_instances'] == 2