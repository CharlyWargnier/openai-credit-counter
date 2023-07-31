import streamlit as st
import openai
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from google.oauth2 import service_account
from datetime import timedelta
import os

from datatoGsheet import *

st.image('https://em-content.zobj.net/thumbs/240/apple/354/abacus_1f9ee.png', width=100)

st.title("OpenAI Credit Counter")

st.write(

    '''

    Welcome to the OpenAI Credit Counter app!

This app offers an easy to use UI to track the number of queries made by app users to OpenAI's GPT-3 model each day. It uses a Google Sheet to monitor daily usage and prevent it from exceeding a set limit. When the daily limit is reached, the app notifies users, allowing them to make more queries.

Simply fork the code and use it for your LLM projects, providing a better LLM experience for your users! 🎈


'''
)

tab1, tab2, tab3= st.tabs(["Community Version", "Enter your own API key", "💡 How to set up your Google Sheet"])

with tab3:

    st.write('')
    st.write('')

    st.write(
        '''


### 📄 Setting Up Google Sheet:
1. **Create a Google Sheet**: Fill with necessary data.
2. **Share It**: Share the sheet with the `client_email` from your `secrets.toml` file.

### 🔑 Setting Up Credentials on Community Cloud:
1. **Create a Service Account**: In [Google Cloud Platform](https://console.developers.google.com/), create a service account with "Editor" permissions for Sheets.
2. **Get JSON Key**: Generate a JSON key and convert it to TOML.
3. **Add Secrets to Streamlit**: In Streamlit's community cloud, paste the TOML content under "Secrets."

### 💻 Local Setup:
1. **Fork and Clone**: Fork the GitHub repo and clone it locally.
2. **Create Secrets File**: Paste TOML content into `.streamlit/secrets.toml`.
3. **Install and Run**: Install dependencies, and run `streamlit run app.py`.

🚨 **Keep It Safe**: Always protect your secrets and never push them to public repositories. Make sure to enable the Google Sheets API in Google Cloud if needed.

''')

with tab1:

    os.environ['OPENAI_API_KEY'] = st.secrets['openai']['OPENAI_API_KEY']
    openai.api_key = os.environ['OPENAI_API_KEY']

    # Function to make a request to the OpenAI API
    @st.cache_data
    def make_request(question_input: str):
        # Make the API call
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": question_input,
                },
                {"role": "user", "content": api_query},
            ],
        )
        return response

    with st.form("my_form"):
        
        system_prompt = st.text_area("Enter your prompt", value='Create a one liner poem', key = 1)

        api_query = openai.api_key

        day = datetime.now().strftime("%Y-%m-%d")
        daily_tokens = get_daily_token_count(day)

        token_cap = 500

        remaining_time = get_remaining_time()
        hours, remainder = divmod(remaining_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        submitted = st.form_submit_button("Submit")

    if submitted:
        if daily_tokens < token_cap:
            response = make_request(system_prompt)

            if response:
                st.write(response["choices"][0]["message"]["content"])

                tokens_used = response["usage"]["total_tokens"]

                # Add data to the Google Sheet
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                add_data_to_sheet("API call", timestamp, day, tokens_used)

                # Update the daily tokens count immediately after the API call
                daily_tokens += tokens_used

                # st.success("API call data added to the Google Sheet")
        else:
            st.info(
                f"⚠️ API call limit exceeded! Come back in **{hours} hours {minutes} minutes** to get free tokens again!"
            )

    used_tokens_pct = get_used_tokens_pct(daily_tokens, token_cap)

    remaining_tokens = token_cap - daily_tokens

    # Create a progress bar for the used tokens
    st.markdown(f" ##### Used tokens for today: `{daily_tokens}`")

    st.progress(min(used_tokens_pct / 100, 1.0))

    st.caption(
        f"`{used_tokens_pct:.0f}%` of the daily allowance of `{token_cap}` tokens has been used. "
        f"`{remaining_tokens}` tokens are remaining for today."
    )


with tab2:

    st.write("Enter your own API key")

    # Input field to accept user's API key
    user_api_key = st.text_input("API Key", type='password')

    if user_api_key:
        # Set up OpenAI API key
        openai.api_key = user_api_key

        # You can now use the user's API key for any OpenAI operations

        # Example: Function to make a request to the OpenAI API
        @st.cache_data
        def make_request_with_user_key(question_input: str):
            # Make the API call
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": question_input,
                    },
                    {"role": "user", "content": question_input},
                ],
            )
            return response

        # You can add more functionality to allow users to make queries using their own API key.
        with st.form("user_form"):
            user_system_prompt = st.text_area("Enter your prompt", value='Create a one liner poem', key = 2)
            user_submitted = st.form_submit_button("Submit")

        if user_submitted:
            response = make_request_with_user_key(user_system_prompt)
            if response:
                st.write(response["choices"][0]["message"]["content"])


