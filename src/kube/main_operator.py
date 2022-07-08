import kopf
import logging
from src.utilities.dates_times import docker_str_to_datetime
from src.docker_imgs.dockerhub_api import img_namespace_for_search_query, get_search_img_dockerhub_api, get_latest_img_date_dockerhub_api, get_version_for_latest_tag
from src.docker_imgs.docker_versions_utilities import perform_automatic_update
from src.kube.kubernetes_api import update_docker_image
from kubernetes import client, config


#TODO: Retrieve user defined checking frequency to set it in the decorator.
#TODO: Logging by e-mail.
#TODO: Logging levels.
#TODO: Parallel updates checking
@kopf.timer('versioninghandlers', interval=600)
def updates_checker(spec, **_) -> None:
    """ This is the operator's heart.
    It is the function responsible of retrieving the deployment's images versions continuously and update/notify the user.

    Returns: None
    """    
    version_frontier = spec['versionsFrontier']
    api_instance = client.CoreV1Api(config.new_client_from_config())
    #Get information for all pods
    resp = api_instance.list_pod_for_all_namespaces()
    #Set the URL needed to communicate with the API for updates beforehand
    for pod in resp.items:
        if 'kube-apiserver' in pod.metadata.name:
            for container in pod.spec.containers:
                if 'kube-apiserver' in container.image:
                    apiserver_url = f'https://{container.liveness_probe.http_get.host}:{container.liveness_probe.http_get.port}'

    #Get namespaces to look at
    namespaces = api_instance.list_namespace()
    native_namespaces = ['kube-system', 'kube-node-lease', 'kube-public']
    namespaces_to_look_at = []
    for namespace in namespaces.items:
        if namespace.metadata.name not in native_namespaces:
            namespaces_to_look_at.append(namespace.metadata.name)

    #Traverse pods' images, obtaining their information and 
    config.load_kube_config()
    appsv1api = client.AppsV1Api()
    for deployment_namespace in namespaces_to_look_at:
        deployments = appsv1api.list_namespaced_deployment(namespace=deployment_namespace)
        for deployment in deployments.items:
            deployment_name = deployment.metadata.name
            for container in deployment.spec.template.spec.containers: 
                curr_img = container.image
                img_name = curr_img.split(':')[0]
                img_version = curr_img.split(':')[1]
                try:
                    #Get the namespace, so we can query the DockerHub API to get the dates of the latest and current versions.
                    img_namespace = img_namespace_for_search_query(get_search_img_dockerhub_api(img_name), img_name)
                except Exception:
                    #The image is not found in DockerHub. Go for the next container.
                    continue
                #Local
                #Get current image date.
                curr_image_date = docker_str_to_datetime(get_latest_img_date_dockerhub_api(img_namespace, img_name, img_version))
                #DockerHub
                #Check on the catalogue of the Docker Hub for the latest image with the name and tag
                latest_image_date = docker_str_to_datetime(get_latest_img_date_dockerhub_api(img_namespace, img_name, 'latest'))
                #Compare
                if curr_image_date == latest_image_date:
                    latest_version_number = get_version_for_latest_tag(img_name, img_namespace)
                    if perform_automatic_update(img_version, latest_version_number, version_frontier):
                        update_docker_image(img_name, deployment_name, deployment_namespace, apiserver_url)
                    else:
                        logging.warning(f"Pod {deployment_name} has an outdated image: {curr_img}")
                else:
                    logging.info('Up to date!')
                