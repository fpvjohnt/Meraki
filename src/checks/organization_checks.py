from typing import Dict, Any, List
from datetime import datetime, timedelta
from src.api.meraki_api import MerakiAPI
from src.utils.logger import logger
from src.utils.exceptions import MerakiHealthCheckError

async def check_organization_admins(api: MerakiAPI, org_id: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Checking organization admins for organization {org_id}")
    result: Dict[str, Any] = {'is_ok': True, 'admin_count': 0, 'issues': []}

    try:
        admins: List[Dict[str, Any]] = await api.get_organization_admins(org_id)
        result['admin_count'] = len(admins)

        if result['admin_count'] > thresholds['max_admins']:
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'medium',
                'category': 'Admin Count',
                'message': f"Number of admins ({result['admin_count']}) exceeds the recommended amount ({thresholds['max_admins']})"
            })
            logger.warning(f"High number of admins for organization {org_id}: {result['admin_count']}")
        
        full_access_admins = [admin for admin in admins if admin.get('orgAccess') == 'full']
        if len(full_access_admins) > thresholds['max_full_admins']:
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'high',
                'category': 'Admin Permissions',
                'message': f"Number of admins with full access ({len(full_access_admins)}) exceeds the recommended amount ({thresholds['max_full_admins']})"
            })
            logger.warning(f"High number of full access admins for organization {org_id}: {len(full_access_admins)}")

        # Check for inactive admins
        inactive_threshold = datetime.now() - timedelta(days=thresholds['inactive_admin_days'])
        inactive_admins = [admin for admin in admins if datetime.fromisoformat(admin['lastActive'].rstrip('Z')) < inactive_threshold]
        if inactive_admins:
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'low',
                'category': 'Inactive Admins',
                'message': f"Found {len(inactive_admins)} inactive admins (last active > {thresholds['inactive_admin_days']} days ago)"
            })
            logger.info(f"Inactive admins found for organization {org_id}: {len(inactive_admins)}")

    except Exception as e:
        logger.error(f"Error checking organization admins for organization {org_id}: {str(e)}")
        raise MerakiHealthCheckError(
            message=f"Failed to check organization admins: {str(e)}",
            category="API Error",
            severity="high"
        )
    
    return result

async def check_organization_inventory(api: MerakiAPI, org_id: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Checking organization inventory for organization {org_id}")
    result: Dict[str, Any] = {'is_ok': True, 'utilization': 0, 'issues': []}

    try:
        inventory: List[Dict[str, Any]] = await api.get_organization_inventory_devices(org_id)
        total_devices = len(inventory)
        used_devices = sum(1 for device in inventory if device.get('networkId') is not None)
        
        result['utilization'] = (used_devices / total_devices) * 100 if total_devices > 0 else 0

        if result['utilization'] > thresholds['inventory_utilization']:
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'medium',
                'category': 'Inventory Utilization',
                'message': f"Inventory utilization ({result['utilization']:.2f}%) exceeds the recommended threshold ({thresholds['inventory_utilization']}%)"
            })
            logger.warning(f"High inventory utilization for organization {org_id}: {result['utilization']:.2f}%")

        unclaimed_devices = [device for device in inventory if device.get('networkId') is None]
        if len(unclaimed_devices) > thresholds['max_unclaimed_devices']:
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'low',
                'category': 'Unclaimed Devices',
                'message': f"Number of unclaimed devices ({len(unclaimed_devices)}) exceeds the recommended amount ({thresholds['max_unclaimed_devices']})"
            })
            logger.info(f"High number of unclaimed devices for organization {org_id}: {len(unclaimed_devices)}")

        # Check for devices with old firmware
        old_firmware_devices = [device for device in inventory if device.get('firmware') and device['firmware'] < thresholds['min_firmware_version']]
        if old_firmware_devices:
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'medium',
                'category': 'Outdated Firmware',
                'message': f"Found {len(old_firmware_devices)} devices with firmware older than {thresholds['min_firmware_version']}"
            })
            logger.warning(f"Devices with old firmware found in organization {org_id}: {len(old_firmware_devices)}")

    except Exception as e:
        logger.error(f"Error checking organization inventory for organization {org_id}: {str(e)}")
        raise MerakiHealthCheckError(
            message=f"Failed to check organization inventory: {str(e)}",
            category="API Error",
            severity="high"
        )

    return result

async def check_organization_licensing(api: MerakiAPI, org_id: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Checking organization licensing for organization {org_id}")
    result: Dict[str, Any] = {'is_ok': True, 'issues': []}

    try:
        licenses: List[Dict[str, Any]] = await api.get_organization_licenses(org_id)

        for license in licenses:
            expiration_date = datetime.fromisoformat(license['expirationDate'].rstrip('Z'))
            days_to_expiration = (expiration_date - datetime.now()).days
            if days_to_expiration < thresholds['license_expiration_warning']:
                result['is_ok'] = False
                result['issues'].append({
                    'severity': 'high' if days_to_expiration < 0 else 'medium',
                    'category': 'License Expiration',
                    'message': f"License {license['id']} will expire in {days_to_expiration} days"
                })
                logger.warning(f"License {license['id']} for organization {org_id} will expire in {days_to_expiration} days")

        # Check for license utilization
        total_licensed_devices = sum(license['deviceCount'] for license in licenses)
        total_used_devices = sum(license['deviceCount'] - license['unusedCount'] for license in licenses)
        license_utilization = (total_used_devices / total_licensed_devices) * 100 if total_licensed_devices > 0 else 0

        if license_utilization > thresholds['license_utilization_warning']:
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'medium',
                'category': 'License Utilization',
                'message': f"License utilization ({license_utilization:.2f}%) is high"
            })
            logger.warning(f"High license utilization for organization {org_id}: {license_utilization:.2f}%")

    except Exception as e:
        logger.error(f"Error checking organization licensing for organization {org_id}: {str(e)}")
        raise MerakiHealthCheckError(
            message=f"Failed to check organization licensing: {str(e)}",
            category="API Error",
            severity="high"
        )

    return result

async def check_organization_alerts(api: MerakiAPI, org_id: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Checking organization alerts for organization {org_id}")
    result: Dict[str, Any] = {'is_ok': True, 'issues': []}

    try:
        alerts: Dict[str, Any] = await api.get_organization_alerts(org_id)

        if not alerts.get('enabled'):
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'high',
                'category': 'Alert Configuration',
                'message': "Organization-wide alerts are disabled"
            })
            logger.warning(f"Organization-wide alerts are disabled for organization {org_id}")

        if not alerts.get('alerts'):
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'medium',
                'category': 'Alert Configuration',
                'message': "No alert configurations found"
            })
            logger.warning(f"No alert configurations found for organization {org_id}")

        # Check for specific important alerts
        important_alerts = ['gateway_down', 'vpn_connectivity_change', 'excessive_dhcp_leases']
        for alert in important_alerts:
            if alert not in [a['type'] for a in alerts.get('alerts', [])]:
                result['is_ok'] = False
                result['issues'].append({
                    'severity': 'medium',
                    'category': 'Alert Configuration',
                    'message': f"Important alert '{alert}' is not configured"
                })
                logger.warning(f"Important alert '{alert}' is not configured for organization {org_id}")

    except Exception as e:
        logger.error(f"Error checking organization alerts for organization {org_id}: {str(e)}")
        raise MerakiHealthCheckError(
            message=f"Failed to check organization alerts: {str(e)}",
            category="API Error",
            severity="high"
        )

    return result