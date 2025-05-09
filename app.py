import pika
import logging
import socket
 
def app():
    """
    Sets up a RabbitMQ consumer that listens for messages on the 'hello' queue.
    """
    # Configure logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
 
    try:
        # Attempt to resolve the hostname
        try:
            rabbitmq_ip = socket.gethostbyname('rabbitmq')
            logger.debug(f"Resolved 'rabbitmq' to: {rabbitmq_ip}")
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_ip))
        except socket.gaierror as e:
            logger.error(f"Failed to resolve 'rabbitmq': {e}")
            print(f"Error: Could not resolve hostname 'rabbitmq'. Exiting.  Check your network configuration and ensure RabbitMQ is running.")
            return  # Important: Exit if we can't connect
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Connection error: {e}")
            print(f"Error connecting to RabbitMQ: {e}")
            return
 
        channel = connection.channel()
        channel.queue_declare(queue='hello')
        logger.debug("Queue 'hello' declared.")
 
        def callback(ch, method, properties, body):
            """
            Callback function to handle received messages.
            """
            logger.info(f"[x] Received {body.decode()}")
            print(f"[x] Received {body.decode()}")  # Keep the print for console output
 
        channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)
 
        logger.info('[*] Waiting for messages. To exit press CTRL+C')
        print('[*] Waiting for messages. To exit press CTRL+C') # Keep print
        channel.start_consuming()  # Start consuming messages
 
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        print(f"An error occurred: {e}") # Keep print
    finally:
        try:
            connection.close()
        except:
            pass
       
 
if __name__ == '__main__':
    app()  # Call the app function.  No arguments are needed.