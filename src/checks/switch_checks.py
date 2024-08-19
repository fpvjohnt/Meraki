from typing import Dict, Any, List
from src.api.meraki_api import MerakiAPI
from src.utils.logger import logger
from src.utils.exceptions import MerakiHealthCheckError

async def check_switch_ports(api: MerakiAPI, switch_serial: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Checking switch ports for switch {switch_serial}")
    result: Dict[str, Any] = {'is_ok': True, 'connected_ports': 0, 'issues': []}

    try:
        ports: List[Dict[str, Any]] = await api.get_device_switch_ports_statuses(switch_serial)
        result['connected_ports'] = len([port for port in ports if port['status'] == 'Connected'])

        if result['connected_ports'] / len(ports) * 100 > thresholds['port_utilization']:
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'medium',
                'category': 'Port Utilization',
                'message': f"Port utilization ({result['connected_ports']/len(ports)*100:.2f}%) exceeds the recommended threshold ({thresholds['port_utilization']}%)"
            })

    except Exception as e:
        logger.error(f"Error checking switch ports for switch {switch_serial}: {str(e)}")
        raise MerakiHealthCheckError(
            message=f"Failed to check switch ports: {str(e)}",
            category="API Error",
            severity="high"
        )

    return result

async def check_switch_stp(api: MerakiAPI, network_id: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Checking switch STP for network {network_id}")
    result: Dict[str, Any] = {'is_ok': True, 'stp_instances': 0, 'issues': []}

    try:
        stp_data: Dict[str, Any] = await api.get_network_switch_stp(network_id)

        result['stp_instances'] = len(stp_data.get('stpInstances', []))

        if result['stp_instances'] > thresholds['stp_instances']:
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'medium',
                'category': 'STP Instances',
                'message': f"Number of STP instances ({result['stp_instances']}) exceeds the recommended amount ({thresholds['stp_instances']})"
            })

        root_bridges = set(instance['rootBridge']['address'] for instance in stp_data.get('stpInstances', []))
        if len(root_bridges) > 1:
            result['is_ok'] = False
            result['issues'].append({
                'severity': 'high',
                'category': 'STP Root Bridge',
                'message': f"Multiple STP root bridges detected: {', '.join(root_bridges)}"
            })

        for instance in stp_data.get('stpInstances', []):
            if instance.get('stpMode') != 'rstp':
                result['is_ok'] = False
                result['issues'].append({
                    'severity': 'medium',
                    'category': 'STP Mode',
                    'message': f"STP instance {instance.get('id')} is not using RSTP mode"
                })

    except Exception as e:
        logger.error(f"Error checking switch STP for network {network_id}: {str(e)}")
        raise MerakiHealthCheckError(
            message=f"Failed to check switch STP: {str(e)}",
            category="API Error",
            severity="high"
        )

    return result