#!/usr/bin/env bash
echo "Input image name"
read img_name
echo "Input image tag"
read img_tag

docker build --no-cache --build-arg=http_proxy=http://128.141.22.113:8080 --build-arg=https_proxy=http://128.141.22.113:8080 -t $img_name:$img_tag .

