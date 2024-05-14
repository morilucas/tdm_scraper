import requests
from bs4 import BeautifulSoup
import pandas as pd
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Function to scrape data from the website
def scrape_data(url):
    # Set up session with retry strategy
    session = requests.Session()
    retry = Retry(
        total=5,  # Total number of retries
        backoff_factor=1,  # A delay between retries
        status_forcelist=[500, 502, 503, 504]  # Retry on these HTTP status codes
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Set headers to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }

    # Send a GET request to the URL
    response = session.get(url, headers=headers)
    response.raise_for_status()  # Check if the request was successful

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all rows with class "schdType1"
    rows = soup.find_all('tr', class_='schdType1')

    # Extract the last <td> of each row and store the text in a list
    data = [row.find_all('td')[-1].get_text(strip=True) for row in rows]

    # Create a DataFrame to store the data
    df = pd.DataFrame(data, columns=['Last TD'])

    # Sort the DataFrame in alphabetical order
    df = df.sort_values(by='Last TD').reset_index(drop=True)

    return df

# Function to compare old and new data
def compare_data(old_df, new_df):
    old_set = set(old_df['Last TD'])
    new_set = set(new_df['Last TD'])

    # Flag new entries
    new_df['New Entry'] = new_df['Last TD'].apply(lambda x: 'Yes' if x not in old_set else 'No')

    return new_df

# Load existing CSV data
csv_filename = 'schedule_data.csv'
try:
    old_df = pd.read_csv(csv_filename)
except FileNotFoundError:
    old_df = pd.DataFrame(columns=['Last TD'])

# URL of the page to scrape
url = "https://selfservice.mypurdue.purdue.edu/prod/BZWSLCSR.P_Prep_Search?term_in=202510&crn_in=15774"

# Scrape current data
new_df = scrape_data(url)

# Compare old and new data
updated_df = compare_data(old_df, new_df)

# Sort updated DataFrame so new entries appear at the top
updated_df = updated_df.sort_values(by=['New Entry', 'Last TD'], ascending=[False, True]).reset_index(drop=True)

# Save the updated DataFrame to the CSV file
updated_df.to_csv(csv_filename, index=False)

print(f"Data updated and saved to {csv_filename}")
