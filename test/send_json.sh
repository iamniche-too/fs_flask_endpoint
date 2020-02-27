#!/bin/bash

ENDPOINT="http://localhost:8080/consumer_reporting_endpoint"
'{"consumer_id": "1", "timestamp": "18-02-2020 15:28", "throughput": "75"}'

echo "Sending JSON to $ENDPOINT"

curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"consumer_id": "1", "timestamp": "18-02-2020 15:28", "throughput": "75"}' \
  $ENDPOINT 
