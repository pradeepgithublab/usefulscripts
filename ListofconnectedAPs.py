import requests

# Credentials
api_token = 'xh9oBdbYQllXCmCh5Ad63h3Y3enrewPWrDD37XpYA5f1ealYTPJQEb2FMkmo0DBi9vFIiLJpNlHd6fM95Zog8e0NldKTnOol'
site_id = '7ddd12b8-7ecf-451f-9f52-88b3b7ae30c3'

# Base URL for Mist API
base_url = "https://api.eu.mist.com/api/v1"

# Headers for authentication
headers = {
    "Authorization": f"Token {api_token}",
    "Content-Type": "application/json"
}

def fetch_access_points():
    try:
        url = f"{base_url}/sites/{site_id}/devices"
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Debug: Print raw response
        print("Raw Response:", response.json())

        devices = response.json()
        access_points = [device for device in devices if device.get('type') == 'ap']

        if access_points:
            print("Connected Access Points:")
            for ap in access_points:
                print(f"Name: {ap.get('name', 'Unknown')}, MAC: {ap['mac']}, Model: {ap['model']}")
        else:
            print("No access points found for the given SiteID.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching access points: {e}")

fetch_access_points()
