import os
import pandas as pd
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")
VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
VAPI_API_BASE_URL = "https://api.vapi.ai"

# Use your specified Excel file path
EXCEL_FILE_PATH = r"C:\Users\Venugopal\Downloads\customer_data.xlsx"  # r"" for raw string to handle backslashes

# This mapping defines how Excel columns map to internal keys used by the script and VAPI prompt
EXCEL_COLUMN_MAPPING = {
    'Customer ID': 'customer_id',
    'Name': 'name',
    'Last Interaction Date': 'last_interaction_date',
    'Balance Due': 'balance_due',
    'Due Date': 'due_date',
    'Status': 'status',
    'Payment Plan': 'payment_plan',
    'Notes from Agent': 'notes_from_agent',
    'Sentiment': 'sentiment',
    'Last Promise to Pay': 'last_promise_to_pay',
    'Payment History': 'payment_history',
    'Risk Level': 'risk_level',
    'Mobile Number': 'phone'
}

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Data Loading ---
customer_df = None


def load_customer_data():
    global customer_df
    try:
        raw_df = pd.read_excel(EXCEL_FILE_PATH)
        print(f"Successfully read Excel file. Columns found: {raw_df.columns.tolist()}")

        renamed_data = {}
        for excel_col_name, internal_key in EXCEL_COLUMN_MAPPING.items():
            if excel_col_name in raw_df.columns:
                renamed_data[internal_key] = raw_df[excel_col_name]
            else:
                print(f"Warning: Column '{excel_col_name}' defined in MAPPING not found in Excel file.")

        if not renamed_data:
            print("Error: No columns from the mapping were found in the Excel file. Cannot proceed.")
            return False

        customer_df = pd.DataFrame(renamed_data)

        if 'customer_id' in customer_df.columns:
            customer_df['customer_id'] = customer_df['customer_id'].astype(str)
        else:
            print("Error: 'Customer ID' (mapped to 'customer_id') column not found or not mapped correctly.")
            return False

        if 'phone' not in customer_df.columns and 'Mobile Number' in EXCEL_COLUMN_MAPPING:
            print(f"Warning: 'Mobile Number' (mapped to 'phone') column not found in Excel or mapping. "
                  "This might be okay if you only rely on the POST request for the number to call, "
                  "but it won't be available as a {{phone}} variable for the VAPI prompt.")

        print("Customer data loaded and columns renamed successfully.")
        print(f"Columns in processed DataFrame: {customer_df.columns.tolist()}")
        if not customer_df.empty:
            print("First few rows of processed data:\n",
                  customer_df.head().to_string())  # .to_string() for better console output
        return True
    except FileNotFoundError:
        print(f"Error: Data file '{EXCEL_FILE_PATH}' not found.")
        return False
    except Exception as e:
        print(f"Error loading customer data: {e}")
        return False


def get_customer_details(customer_id_to_find):
    if customer_df is None:
        if not load_customer_data():
            return None

    customer_id_to_find = str(customer_id_to_find)
    customer_data_row = customer_df[customer_df['customer_id'] == customer_id_to_find]
    if not customer_data_row.empty:
        return customer_data_row.iloc[0].fillna("Not available").to_dict()
    return None


# --- VAPI Call Initiation ---
def initiate_vapi_call(customer_phone_number_to_call,
                       customer_data_vars):  # customer_data_vars will be IGNORED for this test
    if not VAPI_API_KEY or not VAPI_ASSISTANT_ID or not VAPI_PHONE_NUMBER_ID:
        print("Error: VAPI_API_KEY, VAPI_ASSISTANT_ID, or VAPI_PHONE_NUMBER_ID is missing from .env file.")
        return {"error": "VAPI credentials or IDs not configured in .env file"}, 500

    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }

    # TEST PAYLOAD: ABSOLUTELY MINIMAL for POST /call
    # We are OMITTING the 'assistant' object and any 'variables' entirely.
    # This tests if the basic call initiation to the /call endpoint works with assistantId.
    payload = {
        "assistantId": VAPI_ASSISTANT_ID,
        "phoneNumberId": VAPI_PHONE_NUMBER_ID,
        "customer": {
            "number": customer_phone_number_to_call
        }
    }

    print(f"DEBUG: ***** SENDING MINIMAL PAYLOAD (NO VARIABLES, NO ASSISTANT OBJECT) TO /call *****")

    VAPI_CREATE_CALL_ENDPOINT = "https://api.vapi.ai/call"

    print(f"DEBUG: Using VAPI Endpoint: {VAPI_CREATE_CALL_ENDPOINT}")
    print(f"DEBUG: Final payload being sent to VAPI: {payload}")

    try:
        response = requests.post(VAPI_CREATE_CALL_ENDPOINT, json=payload, headers=headers)
        response.raise_for_status()
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        error_message = f"Error calling VAPI: {e}"
        if e.response is not None:
            try:
                error_details = e.response.json()
            except ValueError:
                error_details = e.response.text
            error_message += f" - Status: {e.response.status_code} - Response: {error_details}"
            print(error_message)
            return {"error": "Failed to initiate call via VAPI",
                    "details": error_details}, e.response.status_code if hasattr(e.response, 'status_code') else 500
        else:
            print(error_message)
            return {"error": "Failed to initiate call via VAPI", "details": str(e)}, 500
@app.route('/initiate-call', methods=['POST'])
def handle_initiate_call():
    data = request.json
    if not data or 'customer_id' not in data or 'mobile_number' not in data:
        return jsonify({"error": "Missing customer_id or mobile_number in request"}), 400

    customer_id = data.get('customer_id')
    mobile_number_to_call = data.get('mobile_number')

    if not mobile_number_to_call or not mobile_number_to_call.startswith('+') or not mobile_number_to_call[
                                                                                     1:].isdigit():
        return jsonify({"error": "mobile_number must be in E.164 format (e.g., +12223334444) and provided"}), 400

    if not customer_id:  # Also check if customer_id is provided
        return jsonify({"error": "customer_id must be provided"}), 400

    customer_details = get_customer_details(customer_id)
    if not customer_details:
        return jsonify({"error": f"Customer with ID '{customer_id}' not found or data loading failed"}), 404

    # customer_details already contains the data with internal keys
    vapi_variables = customer_details

    print(f"INFO: Found customer details for ID '{customer_id}': {vapi_variables}")

    vapi_response, status_code = initiate_vapi_call(mobile_number_to_call, vapi_variables)

    return jsonify(vapi_response), status_code


# --- Main ---
if __name__ == '__main__':
    if not load_customer_data():
        print("CRITICAL: Exiting due to data loading issues. Please check Excel file path and column names.")
    else:
        print("Flask app starting...")
        app.run(debug=True, host='0.0.0.0', port=5001)


