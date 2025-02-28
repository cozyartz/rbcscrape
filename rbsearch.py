import requests
import os
import logging
from dotenv import load_dotenv
import time
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

SAM_API_KEY = os.getenv('SAM_API_KEY')
RETABLE_API_KEY = os.getenv('RETABLE_API_KEY')
RETABLE_ID = os.getenv('RETABLE_ID')


# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to fetch data from SAM.gov API
def fetch_sam_gov_data(retries=3, delay=5):
    url = "https://api.sam.gov/opportunities/v2/search"
    headers = {
        "Content-Type": "application/json"
    }
    
    # Calculate date range (last 30 days)
    today = datetime.now()
    posted_to = today.strftime('%m/%d/%Y')
    posted_from = (today - timedelta(days=30)).strftime('%m/%d/%Y')
    
    params = {
        "api_key": SAM_API_KEY,
        "postedFrom": posted_from,
        "postedTo": posted_to,
        "keywords": "Candles procurement,Aromatherapy products,Sustainable candles",
        "limit": "5",
        "offset": "0"
    }
    
    logging.info(f"Requesting data from: {url}")
    logging.info(f"Request parameters: {params}")

    for attempt in range(retries):
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            logging.info("Successfully fetched data from SAM.gov")
            logging.info(f"Response: {response.json()}")
            return response.json().get('opportunitiesData', [])
        elif response.status_code == 500:
            logging.warning(f"Server error (500) on attempt {attempt + 1}/{retries}. Retrying in {delay} seconds...")
            time.sleep(delay)
        else:
            logging.error(f"Error fetching data: {response.status_code} - {response.text}")
            return []
    logging.error("Failed to fetch data from SAM.gov after multiple attempts.")
    return []

# Function to process and send data to Retable
def process_and_send_data():
    logging.info("Starting data processing job...")
    opportunities = fetch_sam_gov_data()
    if opportunities:
        logging.info("Opportunities fetched successfully")
        # Add your code here to process and send data to Retable
    else:
        logging.info("No opportunities found.")
    logging.info("Job completed.")

# Main Execution
if __name__ == '__main__':
    process_and_send_data()
