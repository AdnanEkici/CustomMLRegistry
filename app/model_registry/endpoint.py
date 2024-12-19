from __future__ import annotations

import socket

import pyfiglet
from endpoint_routes import executor
from endpoint_routes import model_bp
from endpoint_routes import registry
from flasgger import Swagger
from flask import Flask
from waitress import serve

app = Flask(__name__)
Swagger(app)

registry.create_tables()

app.config["EXECUTOR_TYPE"] = "process"
executor.init_app(app)

app.register_blueprint(model_bp)

if __name__ == "__main__":
    FIGLET = pyfiglet.figlet_format("ADO-FLOW", font="roman", width=200)
    print(FIGLET)
    print("ADO-FLOW Model Registry is ready.")
    container_ip = socket.gethostbyname(socket.gethostname())
    port = 5000  # Replace with your desired port if different
    print(f"Flask app is running on http://{container_ip}:{port}/")
    serve(app, host="0.0.0.0", port=5000)
