#!/bin/bash

# Endpoint to send GET request
URL1="http://localhost:5020/"
URL2="http://localhost:5020/error"


# Interval in seconds (e.g., send requests every 1-3 seconds)
INTERVAL=$(shuf -i 1-3 -n 1)

while true
do
  # Send GET request
  echo "Sending requests to your app..."
  curl -X GET $URL1 > /dev/null 2>&1
  curl -X GET $URL2 > /dev/null 2>&1

  # Wait for the specified interval
  sleep $INTERVAL
done
