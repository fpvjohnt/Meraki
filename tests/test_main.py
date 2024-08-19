import pytest
import asyncio
from unittest.mock import patch, AsyncMock, mock_open
import yaml
from main import run_health_check, load_config

@pytest.mark.asyncio
async def test_load_config():
    mock_config = {"api_key": "test_key", "organizations": ["org1", "org2"], "thresholds": {}}
    with patch('builtins.open', mock_open(read_data=yaml.dump(mock_config))):
        config = await load_config('mock_path.yaml')
    assert config == mock_config

@pytest.mark.asyncio
async def test_run_health_check():
    mock_config = {
        "api_key": "test_key",
        "organizations": ["org1"],
        "thresholds": {
            "max_admins": 10,
            "max_full_admins": 5,
            "inactive_admin_days": 30,
            "inventory_utilization": 80,
            "max_unclaimed_devices": 5,
            "min_firmware_version": "1.0",
            "stp_instances": 5,
            "port_utilization": 80,
            "ssid_amount": 4,
            "5G Channel Utilization": 50,
            "5G Occurances Warning": 2,
            "5G Occurances Alarm": 4,
            "5G Min TX Power": 10,
            "5G Min Bitrate": 12,
            "5G Max Channel Width": 40
        },
        "api": {"max_retries": 3, "retry_interval": 1}
    }
    
    mock_api = AsyncMock()
    mock_api.get_organization_networks.return_value = [
        {"id": "network1", "name": "Test Network", "productTypes": ["wireless", "switch"]}
    ]
    mock_api.get_organization_inventory_devices.return_value = []
    
    with patch('src.api.meraki_api.MerakiAPI', return_value=mock_api), \
         patch('src.checks.organization_checks.check_organization_admins', return_value={"is_ok": True}), \
         patch('src.checks.organization_checks.check_organization_inventory', return_value={"is_ok": True}), \
         patch('src.checks.network_checks.check_network_health', return_value={"is_ok": True}), \
         patch('src.checks.network_checks.check_network_firmware', return_value={"is_ok": True}), \
         patch('src.checks.network_checks.check_network_devices', return_value={"is_ok": True}), \
         patch('src.checks.wireless_checks.check_wireless_ssids', return_value={"is_ok": True}), \
         patch('src.checks.wireless_checks.check_wireless_rf_profiles', return_value={"is_ok": True}), \
         patch('src.checks.security_checks.check_firewall_rules', return_value={"is_ok": True}), \
         patch('src.checks.security_checks.check_vpn_status', return_value={"is_ok": True}), \
         patch('src.checks.switch_checks.check_vlan_configuration', return_value={"is_ok": True}), \
         patch('src.checks.switch_checks.check_switch_stp', return_value={"is_ok": True}), \
         patch('src.checks.switch_checks.check_switch_ports', return_value={"is_ok": True}), \
         patch('src.checks.switch_checks.check_port_security', return_value={"is_ok": True}):
        
        results = await run_health_check(mock_config)
    
    assert "organizations" in results
    assert "org1" in results["organizations"]
    assert "org_checks" in results["organizations"]["org1"]
    assert "networks" in results["organizations"]["org1"]
    assert "network1" in results["organizations"]["org1"]["networks"]
    assert "network_checks" in results["organizations"]["org1"]["networks"]["network1"]
    assert "switch_checks" in results["organizations"]["org1"]["networks"]["network1"]