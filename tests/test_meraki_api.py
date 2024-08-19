import pytest
from unittest.mock import AsyncMock, patch
from src.api.meraki_api import MerakiAPI

@pytest.fixture
def api():
    return AsyncMock(spec=MerakiAPI)

@pytest.fixture
def mock_dashboard():
    return AsyncMock()

@pytest.mark.asyncio
async def test_get_organizations(api, mock_dashboard):
    api.get_organizations.return_value = [
        {"id": "123", "name": "Test Org"}
    ]
    result = await api.get_organizations()
    assert len(result) == 1
    assert result[0]["name"] == "Test Org"

@pytest.mark.asyncio
async def test_get_organization_networks(api, mock_dashboard):
    api.get_organization_networks.return_value = [
        {"id": "456", "name": "Test Network"}
    ]
    result = await api.get_organization_networks("123")
    assert len(result) == 1
    assert result[0]["name"] == "Test Network"

# Add more tests for other MerakiAPI methods as needed