import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from src.utils.logger import logger
from src.utils.exceptions import MerakiHealthCheckError

class MerakiAPI:
    def __init__(self, api_key: str, max_retries: int = 3, retry_interval: int = 1):
        self.api_key = api_key
        self.base_url = "https://api.meraki.com/api/v1"
        self.max_retries = max_retries
        self.retry_interval = retry_interval

    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        headers = {
            "X-Cisco-Meraki-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        url = f"{self.base_url}/{endpoint}"

        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(method, url, headers=headers, json=data, params=params) as response:
                        response.raise_for_status()
                        return await response.json()
            except aiohttp.ClientError as e:
                logger.warning(f"API request failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise MerakiHealthCheckError(
                        message=f"API request failed after {self.max_retries} attempts: {str(e)}",
                        category="API Error",
                        severity="high"
                    )
                await asyncio.sleep(self.retry_interval)

    # Organizations
    async def get_organizations(self) -> List[Dict[str, Any]]:
        return await self._make_request("GET", "organizations")

    async def get_organization(self, org_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"organizations/{org_id}")

    async def get_organization_admins(self, org_id: str) -> List[Dict[str, Any]]:
        return await self._make_request("GET", f"organizations/{org_id}/admins")

    async def get_organization_inventory_devices(self, org_id: str) -> List[Dict[str, Any]]:
        return await self._make_request("GET", f"organizations/{org_id}/inventoryDevices")

    async def get_organization_licenses(self, org_id: str) -> List[Dict[str, Any]]:
        return await self._make_request("GET", f"organizations/{org_id}/licenses")

    async def get_organization_alerts(self, org_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"organizations/{org_id}/alerts/settings")

    # Networks
    async def get_organization_networks(self, org_id: str) -> List[Dict[str, Any]]:
        return await self._make_request("GET", f"organizations/{org_id}/networks")

    async def get_network(self, network_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"networks/{network_id}")

    async def get_network_devices(self, network_id: str) -> List[Dict[str, Any]]:
        return await self._make_request("GET", f"networks/{network_id}/devices")

    async def get_network_health_alerts(self, network_id: str) -> List[Dict[str, Any]]:
        return await self._make_request("GET", f"networks/{network_id}/health/alerts")

    async def get_network_traffic(self, network_id: str, timespan: int = 7200) -> Dict[str, Any]:
        params = {"timespan": timespan}
        return await self._make_request("GET", f"networks/{network_id}/traffic", params=params)

    # Appliance
    async def get_network_appliance_vlans(self, network_id: str) -> List[Dict[str, Any]]:
        return await self._make_request("GET", f"networks/{network_id}/appliance/vlans")

    async def get_network_appliance_firewall_l3_firewall_rules(self, network_id: str) -> List[Dict[str, Any]]:
        return await self._make_request("GET", f"networks/{network_id}/appliance/firewall/l3FirewallRules")

    async def get_network_appliance_vpn_site_to_site_vpn(self, network_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"networks/{network_id}/appliance/vpn/siteToSiteVpn")

    async def get_network_appliance_security_intrusion(self, network_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"networks/{network_id}/appliance/security/intrusion")

    async def get_network_appliance_content_filtering(self, network_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"networks/{network_id}/appliance/contentFiltering")

    # Switch
    async def get_device_switch_ports(self, serial: str) -> List[Dict[str, Any]]:
        return await self._make_request("GET", f"devices/{serial}/switch/ports")

    async def get_device_switch_ports_statuses(self, serial: str) -> List[Dict[str, Any]]:
        return await self._make_request("GET", f"devices/{serial}/switch/ports/statuses")

    async def get_network_switch_stp(self, network_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"networks/{network_id}/switch/stp")

    async def get_network_switch_mtu(self, network_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"networks/{network_id}/switch/mtu")

    # Wireless
    async def get_network_wireless_ssids(self, network_id: str) -> List[Dict[str, Any]]:
        return await self._make_request("GET", f"networks/{network_id}/wireless/ssids")

    async def get_network_wireless_rf_profiles(self, network_id: str) -> List[Dict[str, Any]]:
        return await self._make_request("GET", f"networks/{network_id}/wireless/rfProfiles")

    async def get_network_wireless_channel_utilization(self, network_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"networks/{network_id}/wireless/channelUtilization")

    async def get_network_wireless_latency_stats(self, network_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"networks/{network_id}/wireless/latencyStats")

    # Clients
    async def get_network_clients(self, network_id: str, timespan: int = 3600) -> List[Dict[str, Any]]:
        params = {"timespan": timespan}
        return await self._make_request("GET", f"networks/{network_id}/clients", params=params)

    # Device Statuses
    async def get_organization_device_statuses(self, org_id: str) -> List[Dict[str, Any]]:
        return await self._make_request("GET", f"organizations/{org_id}/deviceStatuses")

    # Configuration Templates
    async def get_organization_config_templates(self, org_id: str) -> List[Dict[str, Any]]:
        return await self._make_request("GET", f"organizations/{org_id}/configTemplates")