#!/bin/bash

mkdir Downloads
touch Downloads/random_forest_model.pkl

# Start the Python service in the background
echo "Starting the Python service..."
nohup python ./model_registry/endpoint.py > endpoint.log 2>&1 &
PYTHON_PID=$!
echo "Python service started with PID $PYTHON_PID."

sleep 10

echo "Starting Locust load test..."
locust -f tests/endpoint_tests/registry_endpoint_locust.py --host=http://localhost:5000
