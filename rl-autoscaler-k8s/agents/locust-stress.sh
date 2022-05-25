#!/usr/bin/env bash
cd ~/EPI-kube-scaling/Scripts/

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


# rate_3=$(( 3 * $rate ))
# rate_5=$(( 5 * $rate ))
# rate_7=$(( 7 * $rate ))
# rate_9=$(( 9 * $rate ))
# rates=($rate $rate_3 $rate_5 $rate_7 $rate_9 $rate_7 $rate_5 $rate_3)

# for index in ${!rates[@]}; do
#   current_rate=${rates[$index]}
#   locust -f ./locust.py --headless -u 50 -r $current_rate -H ${endpoint}
# done

cd ~/EPI-kube-scaling/Scripts/
locust -f ./locust.py --headless -u $user -r $rate -H $1 -t $runtime