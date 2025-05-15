from flask import Flask, jsonify
import requests
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@app.route('/allData', methods=['GET'])
def proxy_lights():
    temperature_service_url = 'http://host.docker.internal:5050/temps'
    light_service_url = 'http://host.docker.internal:3000/lights/createAndGetData'

    try:
        logger.debug(f"Requesting data from temperature service: {temperature_service_url}")
        temp_response = requests.get(temperature_service_url)
        temp_response.raise_for_status()
        temperature_data = temp_response.json()
        logger.debug("Successfully received data from temperature-service")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error contacting temperature-service: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve data from temperature-service",
            "details": str(e)
        }), 500

    try:
        logger.debug(f"Requesting data from light service: {light_service_url}")
        light_response = requests.get(light_service_url)
        light_response.raise_for_status()
        light_data = light_response.json()
        logger.debug("Successfully received data from light-service")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error contacting light-service: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve data from light-service",
            "details": str(e)
        }), 500

    # Combine both responses
    combined_data = {
        "temperature_data": temperature_data,
        "light_data": light_data
    }

    return jsonify(combined_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)