from typing import Dict, Any, List
from src.api.meraki_api import MerakiAPI
from src.utils.logger import logger
from src.utils.exceptions import MerakiHealthCheckError

async def check_wireless_ssids(api: MerakiAPI, network_id: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Checking wireless SSIDs for network {network_id}")
    result: Dict[str, Any] = {'is_ok': True, 'ssid_count': 0, 'issues': []}

    try:
        ssids: List[Dict[str, Any]] = await api.get_network_wireless_ssids(network_id)
        enabled_ssids = [ssid for ssid in ssids if ssid['enabled']]
        result['ssid_count'] = len(enabled_ssids)
        
        if result['ssid_count'] > thresholds['ssid_amount']:
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'medium',
                'category': 'SSID Configuration',
                'message': f"Number of enabled SSIDs ({result['ssid_count']}) exceeds the recommended amount ({thresholds['ssid_amount']})"
            })

    except Exception as e:
        logger.error(f"Error checking wireless SSID amount for network {network_id}: {str(e)}")
        raise MerakiHealthCheckError(
            message=f"Failed to check wireless SSID amount: {str(e)}",
            category="API Error",
            severity="high"
        )

    return result

async def check_wifi_channel_utilization(api: MerakiAPI, network_id: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Checking wireless channel utilization for network {network_id}")
    result: Dict[str, Any] = {'is_ok': True, 'issues': []}

    try:
        channel_utilization: Dict[str, Any] = await api.get_network_wireless_channel_utilization(network_id)
        
        for ap in channel_utilization.get('utilizationByAp', []):
            for band in ['wifi0', 'wifi1']:  # wifi0 is typically 2.4GHz, wifi1 is 5GHz
                if ap[band].get('utilization', 0) > thresholds['5G Channel Utilization']:
                    result['is_ok'] = False
                    result['issues'].append({
                        'severity': 'high',
                        'category': 'Channel Utilization',
                        'message': f"AP {ap['serial']} has high channel utilization ({ap[band]['utilization']}%) on {band}"
                    })

    except Exception as e:
        logger.error(f"Error checking wireless channel utilization for network {network_id}: {str(e)}")
        raise MerakiHealthCheckError(
            message=f"Failed to check wireless channel utilization: {str(e)}",
            category="API Error",
            severity="high"
        )

    return result

async def check_wireless_rf_profiles(api: MerakiAPI, network_id: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Checking wireless RF profiles for network {network_id}")
    result: Dict[str, Any] = {'is_ok': True, 'issues': []}

    try:
        rf_profiles: List[Dict[str, Any]] = await api.get_network_wireless_rf_profiles(network_id)
        
        for profile in rf_profiles:
            if profile['bandSelection'] == '5 GHz':
                if profile['channelWidth'] > thresholds['5G Max Channel Width']:
                    result['is_ok'] = False
                    result['issues'].append({
                        'severity': 'medium',
                        'category': 'RF Profile',
                        'message': f"5GHz channel width ({profile['channelWidth']}) exceeds the recommended maximum ({thresholds['5G Max Channel Width']})"
                    })
                
                if profile['minBitrate'] < thresholds['5G Min Bitrate']:
                    result['is_ok'] = False
                    result['issues'].append({
                        'severity': 'low',
                        'category': 'RF Profile',
                        'message': f"5GHz minimum bitrate ({profile['minBitrate']}) is below the recommended minimum ({thresholds['5G Min Bitrate']})"
                    })
            
            if profile['bandSelection'] == '2.4 GHz':
                if profile['minBitrate'] < thresholds.get('2.4G Min Bitrate', 0):
                    result['is_ok'] = False
                    result['issues'].append({
                        'severity': 'low',
                        'category': 'RF Profile',
                        'message': f"2.4GHz minimum bitrate ({profile['minBitrate']}) is below the recommended minimum ({thresholds.get('2.4G Min Bitrate', 0)})"
                    })
            
            if not profile.get('perSsidSettings', {}).get('min24'):
                result['is_ok'] = False
                result['issues'].append({
                    'severity': 'medium',
                    'category': 'RF Profile',
                    'message': f"RF profile '{profile['name']}' doesn't have minimum power settings for 2.4GHz"
                })

    except Exception as e:
        logger.error(f"Error checking wireless RF profiles for network {network_id}: {str(e)}")
        raise MerakiHealthCheckError(
            message=f"Failed to check wireless RF profiles: {str(e)}",
            category="API Error",
            severity="high"
        )

    return result