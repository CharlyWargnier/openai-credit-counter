import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from google.oauth2 import service_account
from datetime import timedelta
import streamlit as st
import json

data = st.secrets["gsheets-json"]
# creds = service_account.Credentials.from_service_account_info(data, scopes=scope)

creds = Credentials.from_service_account_info(data)
sheet_id = '14B1X3zsP1-n_XB6WfNqk_hWhWHKtHhwSVF-cix6smiQ'
sheet_name = 'api_test'
scope = ['https://www.googleapis.com/auth/spreadsheets']
creds = service_account.Credentials.from_service_account_info(data, scopes=scope)

# Function to calculate the remaining time until the token limit resets
def get_remaining_time():
    now = datetime.now()
    reset_time = now + timedelta(days=1)
    reset_time = reset_time.replace(hour=0, minute=0, second=0, microsecond=0)
    remaining_time = reset_time - now
    return remaining_time

# Count the number of API calls made in the Streamlit app per day
def count_api_calls():
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(sheet_id).worksheet(sheet_name)

    records = sheet.get_all_records()
    count = len(records)

    return count

# Function to calculate the percentage of used tokens
def get_used_tokens_pct(daily_tokens, token_cap):
    return daily_tokens / token_cap * 100


# Function to add data to the Google Sheet
def add_data_to_sheet(api_call, timestamp, day, tokens_used):
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(sheet_id).worksheet(sheet_name)
    row_data = [api_call, tokens_used, timestamp, day]

    sheet.append_row(row_data)

# Function to get the total number of tokens used in a day
def get_daily_token_count(day):
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(sheet_id).worksheet(sheet_name)

    records = sheet.get_all_records()
    daily_tokens = 0

    for record in records:
        if record['day'] == day and record['tokens_used'] != '':
            daily_tokens += int(record['tokens_used'])  # Convert the value to an integer

    return daily_tokens