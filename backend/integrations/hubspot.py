import json
import secrets
import base64
import asyncio
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
from integrations.integration_item import IntegrationItem
from redis_client import add_key_value_redis, get_value_redis, delete_key_redis

# Constants
CLIENT_ID = "7c50940a-edcd-4cd5-851c-50083a78478c"
CLIENT_SECRET = "2a562e58-3ab6-4fdd-81ac-276ae3283a2b"
REDIRECT_URI = "http://localhost:8000/integrations/hubspot/oauth2callback"
authorization_url = (
    f"https://app.hubspot.com/oauth/authorize?client_id={CLIENT_ID}"
    f"&scope=crm.objects.contacts.read%20crm.objects.companies.read"
    f"&redirect_uri={REDIRECT_URI}"
)

# Encode client credentials
encoded_client_id_secret = base64.b64encode(
    f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
).decode()


# OAuth2 Authorization
async def authorize_hubspot(user_id, org_id):
    state_data = {
        "state": secrets.token_urlsafe(32),
        "user_id": user_id,
        "org_id": org_id,
    }
    encoded_state = base64.urlsafe_b64encode(json.dumps(state_data).encode()).decode()
    await add_key_value_redis(
        f"hubspot_state:{org_id}:{user_id}", json.dumps(state_data), expire=600
    )
    return f"{authorization_url}&state={encoded_state}"


async def oauth2callback_hubspot(request: Request):
    if request.query_params.get("error"):
        raise HTTPException(status_code=400, detail=request.query_params.get("error"))

    code = request.query_params.get("code")
    encoded_state = request.query_params.get("state")

    try:
        state_data = json.loads(base64.urlsafe_b64decode(encoded_state))
    except (ValueError, json.JSONDecodeError):
        raise HTTPException(status_code=400, detail="Invalid state parameter.")

    original_state = state_data.get("state")
    user_id = state_data.get("user_id")
    org_id = state_data.get("org_id")

    saved_state = await get_value_redis(f"hubspot_state:{org_id}:{user_id}")

    if not saved_state or original_state != json.loads(saved_state).get("state"):
        raise HTTPException(status_code=400, detail="State does not match.")

    async with httpx.AsyncClient() as client:
        response, _ = await asyncio.gather(
            client.post(
                "https://api.hubspot.com/oauth/v1/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": REDIRECT_URI,
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            ),
            delete_key_redis(f"hubspot_state:{org_id}:{user_id}"),
        )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to obtain access token.")

    await add_key_value_redis(
        f"hubspot_credentials:{org_id}:{user_id}",
        json.dumps(response.json()),
        expire=600,
    )

    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    return HTMLResponse(content=close_window_script)


async def get_hubspot_credentials(user_id, org_id):
    credentials = await get_value_redis(f"hubspot_credentials:{org_id}:{user_id}")
    if not credentials:
        raise HTTPException(status_code=400, detail="No credentials found.")

    credentials = json.loads(credentials)

    await delete_key_redis(f"hubspot_credentials:{org_id}:{user_id}")
    return credentials


def _recursive_dict_search(data, target_key):
    """Recursively search for a key in a dictionary of dictionaries."""
    if target_key in data:
        return data[target_key]

    for value in data.values():
        if isinstance(value, dict):
            result = _recursive_dict_search(value, target_key)
            if result is not None:
                return result
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    result = _recursive_dict_search(item, target_key)
                    if result is not None:
                        return result
    return None


def create_integration_item_metadata_object(response_json: dict) -> IntegrationItem:
    """Creates an integration metadata object from the response."""
    name = _recursive_dict_search(response_json, "name") or "Unnamed Item"
    parent_id = response_json.get("parent", {}).get("id")

    properties = response_json.get("properties", {})
    firstname = properties.get("firstname")
    lastname = properties.get("lastname")
    email = properties.get("email")

    integration_item_metadata = IntegrationItem(
        id=response_json.get("id"),
        type=response_json.get("type", "unknown"),
        name=name,
        creation_time=response_json.get("createdAt"),
        last_modified_time=response_json.get("updatedAt"),
        parent_id=parent_id,
        firstname=firstname,  # Add firstname
        lastname=lastname,  # Add lastname
        email=email,  # Add email
    )

    return integration_item_metadata


async def get_items_hubspot(credentials: str) -> list[IntegrationItem]:
    """Aggregates all metadata relevant for a HubSpot integration."""
    credentials = json.loads(credentials)
    headers = {
        "Authorization": f"Bearer {credentials.get('access_token')}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.hubapi.com/crm/v3/objects/contacts", headers=headers
        )

    if response.status_code == 200:
        results = response.json().get("results", [])
        list_of_integration_item_metadata = [
            create_integration_item_metadata_object(result) for result in results
        ]
        print(list_of_integration_item_metadata)
        return list_of_integration_item_metadata
    else:
        raise HTTPException(status_code=400, detail="Failed to fetch data from HubSpot")
