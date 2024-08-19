import meraki
from rich import print as pp
from rich.console import Console
from rich.table import Table
from openpyxl import Workbook
from openpyxl.styles import Font, Color
from src.web.models import UserThreshold

def get_user_thresholds(user_id):
    user_thresholds = UserThreshold.query.filter_by(user_id=user_id).all()
    return {threshold.threshold_name: threshold.threshold_value for threshold in user_thresholds}

def run_health_check(config_path, user_id):
    # Load default thresholds
    thresholds = {
        '5G Channel Utilization': 20,
        '5G Occurances Warning': 10,
        '5G Occurances Alarm': 50,
        '5G Min TX Power': 10,
        '5G Min Bitrate': 12,
        '5G Max Channel Width': 40,
        'broadcast_rate': 100,
        'multicast_rate': 100,
        'topology_changes': 10,
        'ssid_amount': 4
    }

    # Override with user-specific thresholds
    user_thresholds = get_user_thresholds(user_id)
    thresholds.update(user_thresholds)

    # Initialize Meraki SDK
    dashboard = meraki.DashboardAPI(output_log=False, suppress_logging=True)
    
    # Load config file
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)

    org_id = config['organization_id']
    org_name = config['organization_name']
    results = {}

    # Run organization checks
    results['org_settings'] = check_org_admins(dashboard, org_id)

    # Get networks
    networks = dashboard.organizations.getOrganizationNetworks(org_id)
    for network in networks:
        network_id = network['id']
        results[network['name']] = {}

        # General checks
        results[network['name']]['network_health_alerts'] = check_network_health_alerts(dashboard, network_id)
        try:
            results[network['name']]['network_firmware_check'] = check_network_firmware(dashboard, network_id)
        except:
            pp(f"[yellow]The network {network_id} has an issue with the firmware upgrade schedule...")

        if "wireless" in network['productTypes']:
            # Wireless checks
            try:
                results[network['name']]['channel_utilization_check'] = check_wifi_channel_utilization(dashboard, network_id, thresholds)
            except:
                pp(f"[yellow]The network {network_id} does not support channel-utilization reporting. It should probably be upgraded...")
            results[network['name']]['rf_profiles_check'] = check_wifi_rf_profiles(dashboard, network_id, thresholds)
            results[network['name']]['ssid_amount_check'] = check_wifi_ssid_amount(dashboard, network_id, thresholds)

        if "switch" in network['productTypes']:
            # Wired checks
            results[network['name']]['port_counters_check'] = check_switch_port_counters(dashboard, network_id, thresholds)
            results[network['name']]['stp_check'] = check_switch_stp(dashboard, network_id)
            results[network['name']]['mtu_check'] = check_switch_mtu(dashboard, network_id)
            try:
                results[network['name']]['storm_control_check'] = check_switch_storm_control(dashboard, network_id)
            except:
                pp(f"[yellow]The network {network_id} does not support storm-control")

    return results

def check_network_health_alerts(dashboard, network_id: str) -> dict:
    print("\n\t\tChecking network health alerts...\n")
    alerts = dashboard.networks.getNetworkHealthAlerts(network_id)
    if len(alerts) == 0:
        pp(f"[green]No network health alerts for network {network_id}")
        return({'is_ok': True})
    else:
        result = {'is_ok': False, 'alert_list': []}
        pp(f"[red]Network alerts detected for network {network_id}")
        for alert in alerts:
            try:
                del alert['scope']['devices'][0]['url']
                del alert['scope']['devices'][0]['mac']
            except:
                pass
            result['alert_list'].append({'severity': alert['severity'], 'category': alert['category'], 'type': alert['type'], 'details': alert['scope']})
            pp(f"[red]Severity: {alert['severity']}\tCategory: {alert['category']}\tType: {alert['type']}")
        return(result)

def check_wifi_channel_utilization(dashboard, network_id: str, thresholds: dict) -> dict:
    print("\n\t\tChecking wifi channel utilization...\n")
    result = {'is_ok': True}
    channel_utilization = dashboard.networks.getNetworkNetworkHealthChannelUtilization(network_id, perPage=100)
    for ap in channel_utilization:
        utilization_list = [ap['wifi1'][util]['utilization'] for util in range(len(ap['wifi1']))]
        exceeded_utilization_list = [utilization for utilization in utilization_list if utilization > thresholds['5G Channel Utilization']]
        if len(utilization_list) == 0:
            pp(f"[yellow]AP {ap['serial']} does not have 5GHz enabled. Skipping...")
        elif len(exceeded_utilization_list) < thresholds['5G Occurances Warning']:
            pp(f"[green]5GHz Channel Utilization exceeded {thresholds['5G Channel Utilization']}% {len(exceeded_utilization_list)} times, with a peak of {max(utilization_list)}% for AP {ap['serial']}")
            result[ap['serial']] = {'is_ok': True, 'utilization': max(utilization_list), 'occurances': len(exceeded_utilization_list)}
            result['is_ok'] = False
        elif len(exceeded_utilization_list) < thresholds['5G Occurances Alarm']:
            pp(f"[dark_orange]5GHz Channel Utilization exceeded {thresholds['5G Channel Utilization']}% {len(exceeded_utilization_list)} times, with a peak of {max(utilization_list)}% for AP {ap['serial']}")
            result[ap['serial']] = {'is_ok': False, 'utilization': max(utilization_list), 'occurances': len(exceeded_utilization_list)}
            result['is_ok'] = False
        else:
            pp(f"[red]5GHz Channel Utilization exceeded {thresholds['5G Channel Utilization']}% {len(exceeded_utilization_list)} times, with a peak of {max(utilization_list)}% for AP {ap['serial']}")
            result[ap['serial']] = {'is_ok': False, 'utilization': max(utilization_list), 'occurances': len(exceeded_utilization_list)}
            result['is_ok'] = False

    # Adding AP names
    network_devices = dashboard.networks.getNetworkDevices(network_id)
    for device in network_devices:
        if device['serial'] in result:
            result[device['serial']]['name'] = device['name']
    return result

# Add other check functions here (check_wifi_rf_profiles, check_wifi_ssid_amount, check_switch_port_counters, etc.)
# Make sure to update these functions to use the 'dashboard' parameter instead of the global variable

def check_network_firmware(dashboard, network_id: str) -> dict:
    result = {'is_ok': True}
    print("\n\t\tChecking Firmware Version...\n")
    firmware = dashboard.networks.getNetworkFirmwareUpgrades(network_id)['products']
    for product in firmware:
        current_version = firmware[product]['currentVersion']['shortName']
        # Looking for the latest stable version
        for version in firmware[product]['availableVersions']:
            if version['releaseType'] == "stable":
                latest_stable_version = version['shortName']
        if current_version == latest_stable_version:
            pp(f"[green]{product.upper()} is running the current stable version ({current_version})")
        elif firmware[product]['nextUpgrade']['time'] != "":
            pp(f"[green]{product.upper()} is not running the current stable version ({current_version}), but an upgrade is scheduled for {firmware[product]['nextUpgrade']['time']}")
        else:
            pp(f"[red]{product.upper()} is not running the current stable version (current: {current_version}, current stable version: {latest_stable_version})")
            result['is_ok'] = False
        result[product] = {'current_version': current_version, 'latest_stable_version': latest_stable_version, 'scheduled_upgrade': firmware[product]['nextUpgrade']['time']}
    return(result)

def check_org_admins(dashboard, org_id: str) -> dict:
    print("\n\t\tAnalyzing organization admins...\n")
    result = {  'is_ok': False,
                'more_than_one_admin': False,
                'users': {},
                'missing_2fa': True,
                'api_calls': 0,
                'using_v0': False
            }
    org_admins = dashboard.organizations.getOrganizationAdmins(org_id)
    for admin in org_admins:
        result['users'][admin['id']] = {'email': admin['email'], 'name': admin['name'], '2fa': admin['twoFactorAuthEnabled'], 'api_calls': 0, 'using_v0': False}
        if admin['twoFactorAuthEnabled'] == False:
            pp(f"[yellow]Missing 2FA for admin {admin['name']} (email: {admin['email']})")
        else:
            pp(f"[green]Admin {admin['name']} (email: {admin['email']}) has 2FA enabled")
    # Filter full right admins (not just read-only or network specific admins)
    full_right_admins = [admin for admin in org_admins if admin['orgAccess'] == 'full']
    if len(full_right_admins) > 1:
        result['more_than_one_admin'] = True
        pp(f"[green]More than one admin has full rights. This is recommended.")
    else:
        pp(f"[red]Only one admin has full rights. It's recommended to have at least one admin with full rights.")
    if result['more_than_one_admin'] == True and result['missing_2fa'] == []:
        result['is_ok'] = True
    else:
        result['is_ok'] = False
    # Check API access
    pp("Fetching the last 1,000 API calls")
    api_requests = dashboard.organizations.getOrganizationApiRequests(org_id, total_pages=1, timespan=1*86400, perPage=1000)
    result['api_calls'] = len(api_requests)
    pp(f"API access usage: {result['api_calls']} API calls during the last week.")
    for request in api_requests:
        result['users'][request['adminId']]['api_calls'] += 1
        if "/v0/" in request['path']:
            result['using_v0'] = True
            if not result['users'][request['adminId']]['using_v0']:
                pp(f"[red]Admin {result['users'][request['adminId']]['name']} (email: {result['users'][request['adminId']]['email']}) is using the v0 API")
            result['users'][request['adminId']]['using_v0'] = True
            result['is_ok'] = False
    return (result)

# You can add the generate_excel_report function here if you want to keep that functionality

if __name__ == '__main__':
    # This block will not be executed when the script is imported as a module
    pass