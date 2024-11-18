import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# Replace with your Mist API credentials
MIST_API_TOKEN = 'xh9oBdbYQllXCmCh5Ad63h3Y3enrewPWrDD37XpYA5f1ealYTPJQEb2FMkmo0DBi9vFIiLJpNlHd6fM95Zog8e0NldKTnOol'
ORG_ID = '15e7597e-9b06-4381-8443-16aba95c5e0d'
BASE_URL = 'https://api.eu.mist.com/api/v1'

# Set up headers for requests
headers = {
    'Authorization': f'Token {MIST_API_TOKEN}'
}

# Function to get all sites in the organization
def get_sites():
    url = f'{BASE_URL}/orgs/{ORG_ID}/sites'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching sites: {response.status_code}, {response.text}")
        return []

# Function to get APs for a specific site that meet the utilization criteria
def get_high_utilization_aps_for_site(site):
    site_id = site['id']
    site_name = site['name']
    url = f'{BASE_URL}/sites/{site_id}/stats/devices'
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        devices = response.json()
        
        # Filter APs based on high CPU and memory utilization
        high_utilization_aps = [
            {
                'Site Name': site_name,
                'AP MAC': device.get('mac'),
                'CPU Utilization (%)': device.get('cpu_util', 0),
                'Memory Utilization (%)': device.get('mem_util', 0),
                'AP Name': device.get('name'),
                'Model': device.get('model')
            }
            for device in devices
            if device.get('type') == 'ap' and device.get('cpu_util', 0) > 50 and device.get('mem_util', 0) > 40
        ]
        
        return high_utilization_aps
    except requests.RequestException as e:
        print(f"Error fetching APs for site {site_name}: {e}")
        return []

# Function to get AP details across the entire organization in parallel
def get_all_high_utilization_aps():
    all_high_utilization_aps = []
    sites = get_sites()
    
    # Use ThreadPoolExecutor to fetch data from multiple sites concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(get_high_utilization_aps_for_site, site): site for site in sites}
        
        for future in as_completed(futures):
            site_high_utilization_aps = future.result()
            all_high_utilization_aps.extend(site_high_utilization_aps)

    return all_high_utilization_aps

# Function to save data to Excel
def save_to_excel(aps_data):
    df = pd.DataFrame(aps_data)
    file_path = 'High_Utilization_APs_Organization.xlsx'
    df.to_excel(file_path, index=False, sheet_name='High Utilization APs')
    print("Data has been saved to High_Utilization_APs_Organization.xlsx")

if __name__ == "__main__":
    aps_data = get_all_high_utilization_aps()
    if aps_data:
        save_to_excel(aps_data)
    else:
        print("No high-utilization AP data to save.")
