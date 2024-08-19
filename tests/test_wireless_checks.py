import pytest
from unittest.mock import AsyncMock, patch
from src.checks.wireless_checks import check_wifi_channel_utilization, check_wireless_rf_profiles, check_wireless_ssids
from src.api.meraki_api import MerakiAPI

@pytest.fixture
def api():
    return AsyncMock(spec=MerakiAPI)

@pytest.fixture
def thresholds():
    return {
        "5G Channel Utilization": 50,
        "5G Occurances Warning": 2,
        "5G Occurances Alarm": 4,
        "5G Min TX Power": 10,
        "5G Min Bitrate": 12,
        "5G Max Channel Width": 40,
        "ssid_amount": 4
    }

@pytest.mark.asyncio
async def test_check_wifi_channel_utilization(api, thresholds):
    api.get_network_wireless_channel_utilization.return_value = {
        "utilizationByAp": [
            {
                "serial": "AP1",
                "wifi0": {"utilization": 30},
                "wifi1": {"utilization": 60}
            },
            {
                "serial": "AP2",
                "wifi0": {"utilization": 20},
                "wifi1": {"utilization": 40}
            }
        ]
    }

    result = await check_wifi_channel_utilization(api, "test_network_id", thresholds)

    assert result["is_ok"] == False
    assert len(result["issues"]) == 1
    assert result["issues"][0]["severity"] == "high"
    assert "AP1" in result["issues"][0]["message"]

@pytest.mark.asyncio
async def test_check_wireless_rf_profiles(api, thresholds):
    api.get_network_wireless_rf_profiles.return_value = [
        {
            "name": "Profile 1",
            "bandSelection": "5 GHz",
            "channelWidth": 80,
            "minBitrate": 10,
            "perSsidSettings": {"min24": 5}
        },
        {
            "name": "Profile 2",
            "bandSelection": "2.4 GHz",
            "minBitrate": 1,
            "perSsidSettings": {}
        }
    ]

    result = await check_wireless_rf_profiles(api, "test_network_id", thresholds)

    assert result["is_ok"] == False
    assert len(result["issues"]) == 3

@pytest.mark.asyncio
async def test_check_wireless_ssids(api, thresholds):
    api.get_network_wireless_ssids.return_value = [
        {"name": "SSID1", "enabled": True},
        {"name": "SSID2", "enabled": True},
        {"name": "SSID3", "enabled": True},
        {"name": "SSID4", "enabled": True},
        {"name": "SSID5", "enabled": True}
    ]

    result = await check_wireless_ssids(api, "test_network_id", thresholds)

    assert result["is_ok"] == False
    assert result["ssid_count"] == 5
    assert len(result["issues"]) == 1