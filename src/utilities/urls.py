from string import Template


dockerhub_api_call_template_specific_tag = Template('https://hub.docker.com/v2/repositories/$namespace/$image_name/tags/$image_tag')
dockerhub_api_call_template_all_tags = Template('https://hub.docker.com/v2/repositories/$namespace/$image_name/tags/?page=$page')
dockerhub_search_api_call = Template('https://hub.docker.com/api/content/v1/products/search?page_size=100&q=$img_name')
dockerhub_cookies = {'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Content-Type': 'application/json',
                    'Referer': 'https://hub.docker.com/search?q=$img_name',
                    'Search-Version': 'v3',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
                    'X-DOCKER-API-CLIENT': 'docker-hub/1511.0.0',
                    'sec-ch-ua': '\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"102\", \"Google Chrome\";v=\"102\"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '\"Linux\"'}
