#!/bin/bash
source ./env/bin/activate
echo "[$(date)] Task Scheduling Service Started."
echo "v0.01"

echo "Scripts found:"
for d in scripts/*
do
    echo -e "\t ${d%/}"
done
echo "-------------------------------------------"


echo "Running Script:"
for d in scripts/*
do
    echo -e "\t ${d%/}"
    sudo python3 $d "config.json" "status.log"
done
echo "[$(date)] Task Completed."