import kopf
from kubernetes import client
from src.kube.kubernetes_api import get_apiserver_url, get_kubernetes_api_instance, get_namespaces_to_look_at
from src.utilities.dates_times import docker_str_to_datetime
from src.docker_imgs.dockerhub_api import get_latest_version_dockerhub, get_updatable_dockerhub_imgs, img_namespace_for_search_query, get_search_img_dockerhub_api, get_latest_img_date_dockerhub_api
from src.utilities.environment_variables import get_refresh_frequency_in_seconds_environment_variable, get_versions_frontier_environment_variable
from src.utilities.versions import get_latest_pep440_updatable_version, get_latest_version, get_newest_docker_updatable_version
from src.utilities.updater import updating_engine
from src.utilities.internet_connection import is_there_internet_connection
from src.utilities.logging_messages import on_create_log, on_delete_log, on_resume_log, on_update_log
from src.gitlab.api import get_all_gitlab_imgs_in_repository, get_gitlab_imgs_tags



@kopf.on.create('versioninghandlers')
def on_create(spec:dict, meta:dict, **kwargs:dict) -> None:
    """ This function is called when a new versioninghandler is created.
    See here for more information -> https://kopf.readthedocs.io/en/stable/handlers/#registering

    Args:
        spec (dict): The spec of the versioninghandler, which contains the information provided by the user in the spec field of the object's yaml file.
        **kwargs (dict): The kwargs of the versioninghandler.
    
    Returns:
        None 
    """    
    on_create_log(spec, meta['name'], meta['name'], kwargs)


@kopf.on.delete('versioninghandlers')
def on_delete(spec:dict, meta:dict, **kwargs:dict) -> None:
    """ This function is called when a versioninghandler is deleted.
    See here for more information -> https://kopf.readthedocs.io/en/stable/handlers/#state-changing-handlers

    Args:
        spec (dict): The spec of the versioninghandler, which contains the information provided by the user in the spec field of the object's yaml file.
        **kwargs (dict): The kwargs of the versioninghandler.
    
    Returns:
        None 
    """    
    on_delete_log(spec, meta['name'], meta['name'], kwargs)


@kopf.on.update('versioninghandlers')
def on_update(spec:dict, meta:dict, **kwargs:dict) -> None:
    """ This function is called when a versioninghandler is updated.
    See here for more information -> https://kopf.readthedocs.io/en/stable/handlers/#state-changing-handlers

    Args:
        spec (dict): The spec of the versioninghandler, which contains the information provided by the user in the spec field of the object's yaml file.
        **kwargs (dict): The kwargs of the versioninghandler.

    Returns:
        None
    """    
    on_update_log(spec, meta['name'], meta['name'], kwargs)


@kopf.on.resume('versioninghandlers')
def on_resume(spec:dict, meta:dict, **kwargs:dict) -> None:
    """ This function is called when a versioninghandler restarts and detects and object that was previously created.
    See here for more information -> https://kopf.readthedocs.io/en/stable/handlers/#resuming-handlers

    Args:
        spec (dict): The spec of the versioninghandler, which contains the information provided by the user in the spec field of the object's yaml file.
        **kwargs (dict): The kwargs of the versioninghandler.

    Returns:
        None
    """    
    on_resume_log(spec, meta['name'], meta['name'], kwargs)


@kopf.timer('versioninghandlers', interval=get_refresh_frequency_in_seconds_environment_variable())
def updates_checker(spec:dict, meta:dict, **_:dict) -> None:
    """ This is the operator's heart.
    It is the function responsible of retrieving the deployment's images versions continuously and update/notify the user.
    See here for more information about how kopf timers work -> https://kopf.readthedocs.io/en/stable/timers/

    Returns: None
    """    
    logs_registry_json_id = meta['name']

    internet_access_available = is_there_internet_connection(logs_registry_json_id)

    #Get container registry to check
    container_registry = spec['containerregistry']
    if container_registry != 'dockerhub' != 'gitlab':
        raise ValueError(f'The container registry specified in the object {meta["name"]} must be either dockerhub or gitlab')

    # Catch object information.
    target_deployment = spec['deployment']
    # Get environment variables values
    version_frontier = get_versions_frontier_environment_variable()

    # Get namespaces to look at
    api_instance = get_kubernetes_api_instance()
    apiserver_url = get_apiserver_url(api_instance)
    namespaces_to_look_at = get_namespaces_to_look_at(api_instance)

    # Traverse pods' images, obtaining their information and 
    #config.load_kube_config()
    appsv1api = client.AppsV1Api()
    for deployment_namespace in namespaces_to_look_at:
        deployments = appsv1api.list_namespaced_deployment(namespace=deployment_namespace)
        for deployment in deployments.items:
            if deployment.metadata.name == target_deployment:
                deployment_name = deployment.metadata.name
                deployment_namespace = deployment.metadata.namespace
                for container in deployment.spec.template.spec.containers: 
                    # Get image names and versions.
                    # Partition is needed for Gitlab versions, which contain the whole URL in the deployment name field.
                    img_partition = container.image.partition('containers/')
                    short_img_name = container.image if img_partition[2] == '' else img_partition[2]
                    img_version = short_img_name.split(':')[1]
                    short_img_name = short_img_name.split(':')[0]
                    full_image_name = short_img_name.split(':')[0] if img_partition[2] == '' else f'{img_partition[0]}containers/{img_partition[2].split(":")[0]}'
                    logs_registry_curr_img_id = f'{deployment_namespace}/{deployment_name}/{short_img_name}:{img_version}'

                    if container_registry == 'gitlab':
                        # All Gitlab's images of the repository
                        gitlab_imgs_list = set(get_all_gitlab_imgs_in_repository(logs_registry_json_id, ''))
                        if short_img_name in gitlab_imgs_list:
                            # Gitlab image
                            img_versions = get_gitlab_imgs_tags(short_img_name, logs_registry_json_id, logs_registry_curr_img_id)
                            latest_version_number = get_latest_version(img_versions, filter=True)
                            latest_updatable_version_number = get_latest_pep440_updatable_version(img_version, img_versions, version_frontier)
                            if latest_updatable_version_number != '' or latest_version_number == 'latest':
                                updating_engine(full_image_name, deployment_name, deployment_namespace, apiserver_url, img_version, \
                                    latest_updatable_version_number, latest_version_number, logs_registry_json_id, logs_registry_curr_img_id)
                    if container_registry == 'dockerhub' and internet_access_available:
                        # Docker image, it requires internet access
                        full_image_namespace = img_namespace_for_search_query(get_search_img_dockerhub_api(full_image_name, logs_registry_json_id, logs_registry_curr_img_id), full_image_name, logs_registry_json_id, logs_registry_curr_img_id)
                        if img_version == 'latest':
                            latest_updatable_version_number = latest_version_number = 'latest'
                        else:
                            available_newer_imgs = get_updatable_dockerhub_imgs(full_image_namespace, full_image_name, img_version, logs_registry_json_id, logs_registry_curr_img_id)
                            latest_version_number = get_latest_version_dockerhub(available_newer_imgs)
                            latest_updatable_version_number = get_newest_docker_updatable_version(img_versions, version_frontier, latest_version_number)
                        # Get current image date.
                        curr_image_date = docker_str_to_datetime(get_latest_img_date_dockerhub_api(full_image_namespace, full_image_name, img_version, logs_registry_json_id, logs_registry_curr_img_id))
                        # Check on the catalogue of the Docker Hub for the latest image with the name and tag
                        latest_image_date = docker_str_to_datetime(get_latest_img_date_dockerhub_api(full_image_namespace, full_image_name, 'latest', logs_registry_json_id, logs_registry_curr_img_id))
                        if latest_updatable_version_number != '':
                            updating_engine(full_image_name, deployment_name, deployment_namespace, apiserver_url, img_version, \
                                latest_updatable_version_number, latest_version_number, logs_registry_json_id, logs_registry_curr_img_id, curr_img_date=curr_image_date, latest_img_date=latest_image_date)
