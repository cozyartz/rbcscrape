# Opportunities Webscraper to Retable

## Overview

This Python script retrieves opportunities data from the SAM.gov API related to contracts and grants in the fields of candles, aromatherapy products, fragrance supplies, wax melts, room sprays, and office/facility supplies. The script downloads any associated resource files, formats the data, and then uploads it to Retable for further processing or tracking.

## Features

- **Data Retrieval:**  
  Fetches opportunity data from SAM.gov based on a dynamic date range (last 30 days).

- **Rate Limiting Handling:**  
  Detects and handles API rate limits by reading the `Retry-After` header and prompting the user for further action.

- **File Downloads:**  
  Downloads resource files associated with each opportunity.

- **Data Formatting:**  
  Formats the fetched data into a structure compatible with Retable.

- **Data Upload:**  
  Sends the formatted data to a specified Retable endpoint.

- **Logging:**  
  Provides real-time logging of the process, including errors and status messages.

## Prerequisites

- **Python 3.6+**
- Required Python packages:
  - `requests`
  - `python-dotenv`
  - Standard libraries: `os`, `logging`, `time`, `datetime`

## Installation

1. **Clone the Repository or Copy the Script:**

   ```bash
   git clone <your-repository-url>
   cd <repository-directory>
