import kopf
from os import popen
from json import loads
from urllib.request import urlopen
from src.utilities.commands import get_all_pods_as_json_command
from src.utilities.urls import _container_id_is_docker
from src.utilities.dates_times import docker_str_to_datetime
from src.docker_imgs.dockerhub_api import img_namespace_for_search_query, get_search_img_dockerhub_api, get_latest_img_date_dockerhub_api


@kopf.timer('prototypecrds', interval=5.0)
def updates_checker(spec, **kwargs):
    imgs = loads(popen(get_all_pods_as_json_command).read())
    for i in imgs['items']:
        for c in i['status']['containerStatuses']:
            #Obtain image name of pod
            curr_img = c['image']
            curr_img_name = curr_img.split(':')[0]
            curr_version = curr_img.split(':')[1]
            container_id = c['imageID']
            if _container_id_is_docker(container_id):
                #It is a Docker image. We get the latest version available and compare, to check if an update must be done.
                #Get the namespace, so we can query the DockerHub API to get the dates of the latest and current versions.
                img_namespace = img_namespace_for_search_query(get_search_img_dockerhub_api(curr_img_name), curr_img_name)
                #Local
                #Get current image date.
                curr_image_date = docker_str_to_datetime(get_latest_img_date_dockerhub_api(img_namespace, curr_img_name, curr_version))
                #DockerHub
                #Check on the catalogue of the Docker Hub for the latest image with the name and tag
                latest_image_date =docker_str_to_datetime(get_latest_img_date_dockerhub_api(img_namespace, curr_img_name, 'latest'))
                #Compare
                if curr_image_date < latest_image_date:
                    print(f"Pod {i['metadata']['name']} has an outdated image: {curr_img}")
