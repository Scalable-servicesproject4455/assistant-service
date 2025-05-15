from flask import Flask, jsonify
import pika
import logging
import socket
import requests
import threading

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def start_consumer():
    """
    Starts a RabbitMQ consumer that listens on the 'hello' queue.
    """
    try:
        try:
            rabbitmq_ip = socket.gethostbyname('rabbitmq')
            logger.debug(f"Resolved 'rabbitmq' to: {rabbitmq_ip}")
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_ip))
        except socket.gaierror as e:
            logger.error(f"Failed to resolve 'rabbitmq': {e}")
            print("Error: Could not resolve hostname 'rabbitmq'. Exiting.")
            return
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Connection error: {e}")
            print(f"Error connecting to RabbitMQ: {e}")
            return

        channel = connection.channel()
        channel.queue_declare(queue='hello')
        logger.debug("Queue 'hello' declared.")

        def callback(ch, method, properties, body):
            logger.info(f"[x] Received {body.decode()}")
            print(f"[x] Received {body.decode()}")

        channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)

        logger.info('[*] Waiting for messages. To exit press CTRL+C')
        print('[*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        print(f"An error occurred: {e}")
    finally:
        try:
            connection.close()
        except:
            pass


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

    combined_data = {
        "temperature_data": temperature_data,
        "light_data": light_data
    }

    return jsonify(combined_data), 200

if __name__ == '__main__':
    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()

    app.run(host='0.0.0.0', port=8080, debug=True)