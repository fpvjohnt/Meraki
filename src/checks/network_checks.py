from typing import Dict, Any
from src.api.meraki_api import MerakiAPI
from src.utils.logger import logger
from src.utils.exceptions import MerakiHealthCheckError

async def check_network_health(api: MerakiAPI, network_id: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Checking network health for network {network_id}")
    result: Dict[str, Any] = {'is_ok': True, 'issues': []}

    try:
        health_alerts: List[Dict[str, Any]] = await api.get_network_health_alerts(network_id)
        
        for alert in health_alerts:
            if alert['severity'] == 'critical':
                result['is_ok'] = False
                result['issues'].append({
                    'severity': 'high',
                    'category': 'Network Health',
                    'message': f"Critical health alert: {alert['category']} - {alert['type']}"
                })
            elif alert['severity'] == 'warning':
                result['is_ok'] = False
                result['issues'].append({
                    'severity': 'medium',
                    'category': 'Network Health',
                    'message': f"Warning health alert: {alert['category']} - {alert['type']}"
                })

    except Exception as e:
        logger.error(f"Error checking network health for network {network_id}: {str(e)}")
        raise MerakiHealthCheckError(
            message=f"Failed to check network health: {str(e)}",
            category="API Error",
            severity="high"
        )

    return result

async def check_network_firmware(api: MerakiAPI, network_id: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Checking network firmware for network {network_id}")
    result: Dict[str, Any] = {'is_ok': True, 'issues': []}

    try:
        firmware_upgrades: Dict[str, Any] = await api.get_network_firmware_upgrades(network_id)
        current_version = firmware_upgrades.get('currentVersion', {}).get('firmware', '')
        last_upgrade = firmware_upgrades.get('lastUpgrade', {})
        last_upgrade_version = last_upgrade.get('toVersion', {}).get('firmware', '')
        last_upgrade_date = last_upgrade.get('releaseDate', '')

        if current_version != last_upgrade_version:
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'medium',
                'category': 'Firmware',
                'message': f"Network is not on the latest firmware version. Current: {current_version}, Latest: {last_upgrade_version}"
            })

    except Exception as e:
        logger.error(f"Error checking network firmware for network {network_id}: {str(e)}")
        raise MerakiHealthCheckError(
            message=f"Failed to check network firmware: {str(e)}",
            category="API Error",
            severity="high"
        )

    return result

async def check_network_devices(api: MerakiAPI, network_id: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Checking network devices for network {network_id}")
    result: Dict[str, Any] = {'is_ok': True, 'issues': []}

    try:
        devices: List[Dict[str, Any]] = await api.get_network_devices(network_id)
        
        for device in devices:
            if device.get('status') != 'online':
                result['is_ok'] = False
                result['issues'].append({
                    'severity': 'high',
                    'category': 'Device Status',
                    'message': f"Device {device.get('name', device.get('serial'))} is {device.get('status')}"
                })

    except Exception as e:
        logger.error(f"Error checking network devices for network {network_id}: {str(e)}")
        raise MerakiHealthCheckError(
            message=f"Failed to check network devices: {str(e)}",
            category="API Error",
            severity="high"
        )

    return result