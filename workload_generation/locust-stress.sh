#!/usr/bin/env bash
# cd ~/EPI-kube-scaling/Scripts/

if [ "$#" -ne 4 ]
then
  echo "Usage: $0 <endpoint> <user> <rate> <runtime>" >&2
  exit 1
fi

# Get the directory of this script
script_dir=$(dirname "$(readlink -f "$0")")

endpoint=$1
user=$2
rate=$3
runtime=$4

# cd ~/EPI-kube-scaling/Scripts/
locust -f ./locust.py --headless -u $user -r $rate -H $1 -t $runtime