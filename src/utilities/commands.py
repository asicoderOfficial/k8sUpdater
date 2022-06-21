import json
from string import Template
import os


get_all_pods_as_json_command = 'kubectl get pods -o json'
get_all_pods_as_json_all_namespaces_command = 'kubectl get pods --all-namespaces -o json '
get_all_pods_for_namespace_as_json_command = Template('kubectl get pods --namespace=$namespace -o json')
search_dockerhub_command = Template(f"curl -s 'https://hub.docker.com/api/content/v1/products/search?page_size=100&q=$img_name' \
                    -H 'Accept: application/json' \
                    -H 'Accept-Language: en-US,en;q=0.9' \
                    -H 'Connection: keep-alive' \
                    -H 'Content-Type: application/json' \
                    -H 'Referer: https://hub.docker.com/search?q=$img_name' \
                    -H 'Search-Version: v3' \
                    -H 'Sec-Fetch-Dest: empty' \
                    -H 'Sec-Fetch-Mode: cors' \
                    -H 'Sec-Fetch-Site: same-origin' \
                    -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36' \
                    -H 'X-DOCKER-API-CLIENT: docker-hub/1511.0.0' \
                    -H 'sec-ch-ua: \" Not A;Brand\";v=\"99\", \"Chromium\";v=\"102\", \"Google Chrome\";v=\"102\"' \
                    -H 'sec-ch-ua-mobile: ?0' \
                    -H 'sec-ch-ua-platform: \"Linux\"' \
                    --compressed")
