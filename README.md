                                                                                                                                                      Of course. Here is a professional and concise README file suitable for a GitHub repository.

VAPI.ai Outbound Calling Agent

This project is a Python Flask server that initiates outbound phone calls to customers using the VAPI.ai voice AI platform. It reads customer information from a local Excel file and uses a simple API endpoint to trigger a call to a specific customer.

Features

Data-Driven Calls: Pulls customer data from a local Excel file.

API Controlled: Initiates calls via a simple POST request.

Configurable: Easily set API keys, VAPI IDs, and file paths using an environment file.

Dynamic: Looks up specific customer details by their ID to use in the call.

Getting Started

Follow these instructions to get the project set up and running on your local machine.

1. Prerequisites

Python 3.7+

pip for package installation

2. Installation & Setup

Clone the Repository

Generated bash
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name


Install Dependencies
Create a requirements.txt file with the following content:

Generated code
pandas
Flask
requests
python-dotenv
openpyxl
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
IGNORE_WHEN_COPYING_END

Then, install the dependencies using pip:

Generated bash
pip install -r requirements.txt
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Create .env File
Create a file named .env in the root project directory. This file will store your secret credentials. Add your VAPI keys and IDs to it:

Generated env
VAPI_API_KEY="your_vapi_api_key_here"
VAPI_ASSISTANT_ID="your_vapi_assistant_id_here"
VAPI_PHONE_NUMBER_ID="your_vapi_phone_number_id_here"
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Env
IGNORE_WHEN_COPYING_END

VAPI_API_KEY: Your secret API key from the VAPI dashboard.

VAPI_ASSISTANT_ID: The ID of the VAPI assistant you want to handle the call.

VAPI_PHONE_NUMBER_ID: The ID of the phone number you've purchased on VAPI that will be used to make the outbound call.

Prepare the Customer Data File

Place your customer data in an Excel file (e.g., customer_data.xlsx).

Update the EXCEL_FILE_PATH variable in the Python script to point to your file's location.

Ensure your Excel file contains columns that match the EXCEL_COLUMN_MAPPING in the script. The most critical columns are Customer ID and Mobile Number.

Running the Application

To start the server, run the main Python script from your terminal:

Generated bash
python your_script_name.py
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

The server will start, load the customer data from your Excel file, and listen for incoming requests on http://localhost:5001.

How to Trigger a Call

To initiate a call, send a POST request to the /initiate-call endpoint. The request body must be a JSON object containing the customer_id and the mobile_number to call.

Example using cURL

Here is an example of how to trigger a call from your command line using curl:

Generated bash
curl -X POST http://localhost:5001/initiate-call \
-H "Content-Type: application/json" \
-d '{
    "customer_id": "101",
    "mobile_number": "+15551234567"
}'
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

customer_id: The ID of the customer as it appears in your Excel file. The script will use this to look up their details.

mobile_number: The destination phone number in E.164 format (must include the + and country code).

The server will look up the customer's details, place the call via the VAPI.ai API, and return VAPI's response confirming the call has been initiated.

