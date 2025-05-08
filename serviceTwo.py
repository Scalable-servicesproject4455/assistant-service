from flask import Flask, request, jsonify
from flask_cors import CORS
import requests


app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from your React frontend

API_URL = "https://api.stlouisfed.org/fred/series/observations"
API_KEY = "ad68f7b173ee40ece202d52b24f22f60"
DATABRICKS_URL = "https://adb-3991471668185668.8.azuredatabricks.net/ajax-serving-endpoints/prophet-model-01/invocations"

# Static headers (ensure they don't expire, or use a secure way to manage tokens)
HEADERS = {
    "Cookie": "workspace-url=adb-3991471668185668.8.azuredatabricks.net; JSESSIONID=login-676d84f54-9wbl8-4i5dth6co1u3wuno27xpdyvh.login-676d84f54-9wbl8-",
    "x-csrf-token": "f285614f-10db-4d33-aa16-0d4ab77400e2",
    "Content-Type": "application/json"
}

@app.route('/')
def forexcast():
    return "Hello from Flask!"

@app.route('/api/hello2', methods=['GET'])
def hello():
    return jsonify({"message": "Hello from Service Two!"})

@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    return jsonify({"received": data}), 200

@app.route("/api/exchange-rate", methods=["GET"])
def get_exchange_rate():
    try:
        params = {
            "series_id": "DEXUSEU",
            "api_key": API_KEY,
            "file_type": "json",
            "observation_start": "2024-01-01",
            "observation_end": "2024-12-31",
            "sort_order": "asc"
        }
        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

        return jsonify(response.json())  # Return the API response to frontend
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to fetch exchange rate", "details": str(e)}), 500

@app.route('/api/genai', methods=['POST'])
def genai_response():
    data = request.get_json()
    prompt = data.get("prompt", "")
    response = insights.generate_response(prompt)
    response_text = str(response.content)  # Convert to string

    return jsonify({"response": response_text})

@app.route('/send-alert', methods=['POST'])
def send_alert():
    data = request.json  # Get JSON request body
    payload = MSTeamIntegration.prepare_teams_payload(data) 
    send_email(triggerEmail.prepare_email_payload())
    return MSTeamIntegration.send_teams_alert(payload) 

@app.route("/proxy", methods=["POST"])
def proxy_request():
    try:
        req_data = request.get_json()  # Get request body from frontend
        response = requests.post(DATABRICKS_URL, headers=HEADERS, json=req_data)

        # Return Databricks response to frontend
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

@app.route('/api/call-s1', methods=['GET'])
def call_s1():
    try:
        response = requests.get("http://127.0.0.1:5000/api/hello")
        return jsonify({
            "status": "success",
            "data_from_s1": response.json()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def send_email(data):
    # data = request.json
    #paylaod = triggerEmail.prepare_email_payload(data)  # Prepare email payload
    return triggerEmail.send_email(data)

# GET API: Fetch Data
@app.route('/data', methods=['GET'])
def get_data():
    result, status = dbDataHandlers.get_data_from_db()
    return jsonify(result), status

# POST API: Upsert Data
@app.route('/data', methods=['POST'])
def upsert_data():
    data = request.json
    result, status = dbDataHandlers.upsert_data_to_db(data)
    return jsonify(result), status


@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    status = customPdfHandler.store_pdfs_in_db()
    if status:
        return jsonify({"message": "PDF uploaded successfully!"}), 200
    else:
        return jsonify({"error": "Failed to upload PDF"}), 500
 
    
@app.route('/get-pdf/<pdf_id>', methods=['GET'])
def get_pdf(pdf_id):
    response = customPdfHandler.get_pdf_from_DB(pdf_id)
    if response:
        return response
    else:
        return jsonify({"error": "Failed to retrieve PDF"}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
