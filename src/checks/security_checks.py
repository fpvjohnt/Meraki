from typing import Dict, Any, List
from src.api.meraki_api import MerakiAPI
from src.utils.logger import logger
from src.utils.exceptions import MerakiHealthCheckError

async def check_firewall_rules(api: MerakiAPI, network_id: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Checking firewall rules for network {network_id}")
    result: Dict[str, Any] = {'is_ok': True, 'issues': []}

    try:
        firewall_rules: List[Dict[str, Any]] = await api.get_network_appliance_firewall_l3_firewall_rules(network_id)
        
        if len(firewall_rules) > thresholds['max_firewall_rules']:
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'medium',
                'category': 'Firewall Rules',
                'message': f"Number of firewall rules ({len(firewall_rules)}) exceeds the recommended amount ({thresholds['max_firewall_rules']})"
            })
        
        for rule in firewall_rules:
            if rule['policy'] == 'allow' and rule['srcPort'] == 'Any' and rule['destPort'] == 'Any':
                result['is_ok'] = False
                result['issues'].append({
                    'severity': 'high',
                    'category': 'Firewall Rules',
                    'message': f"Overly permissive rule found: {rule['comment'] if 'comment' in rule else 'Unnamed rule'}"
                })
            
            if rule['policy'] == 'allow' and (rule['srcCidr'] == 'Any' or rule['destCidr'] == 'Any'):
                result['is_ok'] = False
                result['issues'].append({
                    'severity': 'medium',
                    'category': 'Firewall Rules',
                    'message': f"Broad CIDR range in allow rule: {rule['comment'] if 'comment' in rule else 'Unnamed rule'}"
                })

    except Exception as e:
        logger.error(f"Error checking firewall rules for network {network_id}: {str(e)}")
        raise MerakiHealthCheckError(
            message=f"Failed to check firewall rules: {str(e)}",
            category="API Error",
            severity="high"
        )

    return result

async def check_vpn_status(api: MerakiAPI, network_id: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Checking VPN status for network {network_id}")
    result: Dict[str, Any] = {'is_ok': True, 'issues': []}

    try:
        vpn_status: Dict[str, Any] = await api.get_network_appliance_vpn_site_to_site_vpn(network_id)
        
        if vpn_status['mode'] == 'none':
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'low',
                'category': 'VPN Configuration',
                'message': "VPN is not configured for this network"
            })
            return result

        if vpn_status['mode'] == 'spoke':
            for hub in vpn_status['hubs']:
                if hub['hubId'] == 'default':
                    continue  # Skip the default hub
                if not hub['useDefaultRoute']:
                    result['is_ok'] = False
                    result['issues'].append({
                        'severity': 'medium',
                        'category': 'VPN Configuration',
                        'message': f"VPN hub {hub['hubId']} is not set to use default route"
                    })

        # Check VPN subnet configuration
        subnets = vpn_status.get('subnets', [])
        if not subnets:
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'medium',
                'category': 'VPN Configuration',
                'message': "No subnets configured for VPN"
            })

    except Exception as e:
        logger.error(f"Error checking VPN status for network {network_id}: {str(e)}")
        raise MerakiHealthCheckError(
            message=f"Failed to check VPN status: {str(e)}",
            category="API Error",
            severity="high"
        )

    return result

async def check_intrusion_prevention(api: MerakiAPI, network_id: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Checking intrusion prevention settings for network {network_id}")
    result: Dict[str, Any] = {'is_ok': True, 'issues': []}

    try:
        intrusion_settings: Dict[str, Any] = await api.get_network_appliance_security_intrusion(network_id)
        
        if not intrusion_settings['mode'] == 'prevention':
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'high',
                'category': 'Intrusion Prevention',
                'message': f"Intrusion prevention mode is set to {intrusion_settings['mode']}, not 'prevention'"
            })
        
        if intrusion_settings['idsRulesets'] != 'balanced':
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'medium',
                'category': 'Intrusion Prevention',
                'message': f"IDS ruleset is set to {intrusion_settings['idsRulesets']}, not 'balanced'"
            })

    except Exception as e:
        logger.error(f"Error checking intrusion prevention settings for network {network_id}: {str(e)}")
        raise MerakiHealthCheckError(
            message=f"Failed to check intrusion prevention settings: {str(e)}",
            category="API Error",
            severity="high"
        )

    return result

async def check_content_filtering(api: MerakiAPI, network_id: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Checking content filtering settings for network {network_id}")
    result: Dict[str, Any] = {'is_ok': True, 'issues': []}

    try:
        content_filtering: Dict[str, Any] = await api.get_network_appliance_content_filtering(network_id)
        
        if not content_filtering['urlCategoryListSize'] == 'fullList':
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'medium',
                'category': 'Content Filtering',
                'message': f"URL category list size is set to {content_filtering['urlCategoryListSize']}, not 'fullList'"
            })
        
        if not content_filtering['blockedUrlCategories']:
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'low',
                'category': 'Content Filtering',
                'message': "No URL categories are blocked"
            })

    except Exception as e:
        logger.error(f"Error checking content filtering settings for network {network_id}: {str(e)}")
        raise MerakiHealthCheckError(
            message=f"Failed to check content filtering settings: {str(e)}",
            category="API Error",
            severity="high"
        )

    return result