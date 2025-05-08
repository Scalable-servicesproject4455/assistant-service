from flask import Flask, jsonify

import requests
 
app = Flask(__name__)
 
@app.route('/api/call-ms1', methods=['GET'])

def call_microservice1():

    try:

        res = requests.get("http://microservice-1:5000/api/hello")

        return jsonify({"received": res.json()})

    except Exception as e:

        return jsonify({"error": str(e)})
 
if __name__ == '__main__':

    app.run(host='0.0.0.0', port=8080)

 