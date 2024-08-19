import asyncio
import yaml
import argparse
from typing import Dict, Any, List
from src.api.meraki_api import MerakiAPI
from src.checks import network_checks, organization_checks, switch_checks, wireless_checks, security_checks
from src.utils.logger import logger
from src.utils.exceptions import MerakiHealthCheckError
from src.utils.report_generator import ReportGenerator

async def load_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

async def run_network_checks(api: MerakiAPI, network_id: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    results = {}
    results['health'] = await network_checks.check_network_health(api, network_id, thresholds)
    results['firmware'] = await network_checks.check_network_firmware(api, network_id, thresholds)
    results['devices'] = await network_checks.check_network_devices(api, network_id, thresholds)
    results['wireless_ssids'] = await wireless_checks.check_wireless_ssids(api, network_id, thresholds)
    results['wireless_rf_profiles'] = await wireless_checks.check_wireless_rf_profiles(api, network_id, thresholds)
    results['firewall_rules'] = await security_checks.check_firewall_rules(api, network_id, thresholds)
    results['vpn_status'] = await security_checks.check_vpn_status(api, network_id, thresholds)
    results['vlan_configuration'] = await switch_checks.check_vlan_configuration(api, network_id, thresholds)
    return results

async def run_organization_checks(api: MerakiAPI, org_id: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    results = {}
    results['admins'] = await organization_checks.check_organization_admins(api, org_id, thresholds)
    results['inventory'] = await organization_checks.check_organization_inventory(api, org_id, thresholds)
    results['licensing'] = await organization_checks.check_organization_licensing(api, org_id, thresholds)
    return results

async def run_switch_checks(api: MerakiAPI, network_id: str, switch_serials: List[str], thresholds: Dict[str, Any]) -> Dict[str, Any]:
    results = {}
    results['stp'] = await switch_checks.check_switch_stp(api, network_id, thresholds)
    results['ports'] = {}
    results['port_security'] = {}
    for serial in switch_serials:
        results['ports'][serial] = await switch_checks.check_switch_ports(api, serial, thresholds)
        results['port_security'][serial] = await switch_checks.check_port_security(api, serial, thresholds)
    return results

async def run_health_check(config: Dict[str, Any]) -> Dict[str, Any]:
    api = MerakiAPI(config['api_key'], config['api']['max_retries'], config['api']['retry_interval'])
    results = {'organizations': {}}

    async def check_network(network: Dict[str, Any], org_id: str):
        network_id = network['id']
        logger.info(f"Running checks for network {network_id}")
        try:
            return {
                'network_checks': await run_network_checks(api, network_id, config['thresholds']),
                'switch_checks': await run_switch_checks(api, network_id, network.get('switchSerials', []), config['thresholds'])
            }
        except MerakiHealthCheckError as e:
            logger.error(f"Error running checks for network {network_id}: {str(e)}")
            return {'error': str(e)}

    for org_id in config['organizations']:
        logger.info(f"Running checks for organization {org_id}")
        try:
            org_checks = await run_organization_checks(api, org_id, config['thresholds'])
            networks = await api.get_organization_networks(org_id)
            
            network_results = await asyncio.gather(*[check_network(network, org_id) for network in networks])
            
            results['organizations'][org_id] = {
                'org_checks': org_checks,
                'networks': {network['id']: result for network, result in zip(networks, network_results)}
            }
        except MerakiHealthCheckError as e:
            logger.error(f"Error running checks for organization {org_id}: {str(e)}")
            results['organizations'][org_id] = {'error': str(e)}

    return results

async def main():
    parser = argparse.ArgumentParser(description="Meraki Health Check Tool")
    parser.add_argument("-c", "--config", default="config.yaml", help="Path to the configuration file")
    parser.add_argument("-o", "--output", default="health_check_report", help="Path to the output report file (without extension)")
    parser.add_argument("--format", choices=["txt", "html"], default="txt", help="Output format (txt or html)")
    args = parser.parse_args()

    try:
        config = await load_config(args.config)
        results = await run_health_check(config)
        
        if args.format == "txt":
            report = ReportGenerator.generate_text_report(results)
            output_file = f"{args.output}.txt"
        else:
            report = ReportGenerator.generate_html_report(results)
            output_file = f"{args.output}.html"
        
        # Save the report to a file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Health check completed successfully. Report saved to {output_file}")
    except Exception as e:
        logger.error(f"An error occurred during the health check: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())