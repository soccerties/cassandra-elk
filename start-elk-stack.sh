#!/bin/bash

export CLIENT_DIAG_PATH=$1
source ./.env

check_kibana_status() {
  for i in {1..30}; do
    kibana_status=`curl -sL -w "%{http_code}\\n" "http://localhost:5601/status" -o /dev/null`
    if [ $kibana_status == "200" ]; then
      echo ""
      break
    else
      if [ ${i} == "30" ]; then
        kibana_timeout
      fi
      sleep 2
      printf "."
    fi
  done
}

import_kibana_dashboards() {
  for f in ./kibana/dashboards/*.json
  do
    curl -X POST "http://127.0.0.1:5601/api/kibana/dashboards/import" -H 'kbn-xsrf: true' -H 'Content-Type: application/json' -d @"$f" -s -o /dev/null
  done
}

kibana_timeout() {
  echo ""
  echo "Timed out while waiting for Kibana to initialize."
  echo "Try rerunning the script"
  exit 1
}

echo "Starting containers"

docker-compose up -d

sleep 3

# elasticsearch files are created by dockerd (root) but the container runs as current user
# So fix perms and restart any containers not running
sudo chown -R `whoami`:`whoami` $CLIENT_DIAG_PATH
sudo chmod -R 777 $CLIENT_DIAG_PATH

docker-compose up -d

echo "Waiting for Kibana"
check_kibana_status

echo "Importing dashboards"
import_kibana_dashboards

echo "containers status"
docker-compose ps

echo ""
echo ""
echo "Visit http://<ip address>:5601 to use Kibana" 
echo "Rerun the script if there's any containers not running."
