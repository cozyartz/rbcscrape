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

# Function to handle rate limiting with dynamic wait time and user input
def handle_rate_limit(response):
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        wait_time = int(retry_after)
        logging.warning(f"Rate limit exceeded. Waiting for {wait_time} seconds before retrying...")
    else:
        wait_time = 60  # Start with 60 seconds instead of 60 minutes
        logging.warning("Rate limit exceeded. No Retry-After header found. Waiting for 60 seconds before retrying...")

    # Ask user if they want to wait or exit
    user_input = input(f"Rate limit hit. Wait for {wait_time} seconds or press 'q' to quit: ").strip().lower()
    if user_input == 'q':
        logging.info("Exiting due to user request.")
        exit(0)
    
    time.sleep(wait_time)

# Updated fetch_sam_gov_data function to handle dynamic rate limiting
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
        "keywords": "Candles,Aromatherapy products,fragrance supplies,Wax melts and room sprays,Office and facility supplies",
        "offset": "0"
    }
    
    logging.info(f"Requesting data from: {url}")
    logging.info(f"Request parameters: {params}")

    for attempt in range(retries):
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            logging.info("Successfully fetched data from SAM.gov")
            return response.json().get('opportunitiesData', [])
        elif response.status_code == 429:  # Handle rate limit error
            handle_rate_limit(response)
        elif response.status_code == 500:
            logging.warning(f"Server error (500) on attempt {attempt + 1}/{retries}. Retrying in {delay} seconds...")
            time.sleep(delay)
        else:
            logging.error(f"Error fetching data: {response.status_code} - {response.text}")
            return []
    logging.error("Failed to fetch data from SAM.gov after multiple attempts.")
    return []


# Function to download files from resource links
def download_file(file_url, file_name):
    try:
        response = requests.get(file_url)
        if response.status_code == 200:
            with open(file_name, 'wb') as file:
                file.write(response.content)
            logging.info(f"Downloaded file: {file_name}")
            return file_name
        else:
            logging.error(f"Failed to download file: {file_url}")
            return None
    except Exception as e:
        logging.error(f"Error downloading file: {e}")
        return None

# Function to format data for Retable and handle file uploads
def format_data_for_retable(opportunities):
    formatted_data = []
    for item in opportunities:
        file_urls = item.get("resourceLinks") or []
        file_paths = []
        for file_url in file_urls:
            file_name = file_url.split('/')[-1]
            file_path = download_file(file_url, file_name)
            if file_path:
                file_paths.append(file_path)
        formatted_data.append({
            "Job Title": item.get("title", ""),
            "Description": item.get("description", ""),
            "Deadline": item.get("responseDeadLine", ""),
            "Link to Job": item.get("uiLink", ""),
            "Category": item.get("type", ""),
            "Files": ", ".join(file_paths)
        })
    return formatted_data

# Function to send data to Retable including file uploads
def send_to_retable(data):
    url = f"https://api.retable.io/v1/public/retable/{RETABLE_ID}/row"
    headers = {
        "Authorization": f"Bearer {RETABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    for row in data:
        payload = {
            "columns": row
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            logging.info("Row successfully added to Retable.")
        else:
            logging.error(f"Error adding row to Retable: {response.status_code} - {response.text}")

# Function to process and send data to Retable
def process_and_send_data():
    logging.info("Starting data processing job...")
    opportunities = fetch_sam_gov_data()
    if opportunities:
        logging.info("Opportunities fetched successfully")
        formatted_data = format_data_for_retable(opportunities)
        send_to_retable(formatted_data)
    else:
        logging.info("No opportunities found.")
    logging.info("Job completed.")

# Main Execution
if __name__ == '__main__':
    process_and_send_data()

