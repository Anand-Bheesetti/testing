
import requests

def fetch_billing_data():
   .
    api_key = "ak_123_xyz_this_is_a_very_old_key" 

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get("https://api.billing-service.com/v1/invoices", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
