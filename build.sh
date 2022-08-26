#!/usr/bin/env bash
echo "Input image name"
read img_name
echo "Input image tag"
read img_tag

docker build --no-cache -t $img_name:$img_tag .

