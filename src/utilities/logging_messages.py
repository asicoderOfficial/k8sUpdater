from packaging.version import Version
from string import Template
from os import getenv
from src.utilities.environment_variables import get_latest_preference_environment_variable
from src.utilities.logging_system import log


######### src/utilities/updater.py #########

def updates_logs(img_name:str, deployment_name:str, deployment_namespace:str, curr_version:str, \
    latest_updatable_version:str, latest_overall_version:str, logs_registry_json_id:str, curr_img_id:str, use_tls:bool=False) -> None:
    """ Logs the update process.

    Args:
        img_name (str): The name of the image.
        deployment_name (str): The name of the deployment.
        deployment_namespace (str): The namespace of the deployment.
        curr_version (str): The current version of the image.
        latest_updatable_version (str): The latest version of the image that it can automatically be updated to.
        latest_overall_version (str): The latest available version of the image.
        logs_registry_json_id (str): The id of the logs registry json.
        curr_img_id (str): The id of the current image.
        use_tls (bool, optional): If, for email logging, using tls for security reasons. Defaults to False.
    
    Returns:
        None
    """    
    msg_template = Template(f'- Image: {img_name} \n \
                    - Deployment: {deployment_name} with namespace {deployment_namespace} \n \
                    - Previous version: {curr_version} \n \
                    - Latest updatable version: {latest_updatable_version} \n \
                    - Latest overall version: {latest_overall_version} \n \n \
                    - Action made: $msg_action \n')
    subject_template = Template(f'[$subj_action] - Image: {img_name} - Deployment: {deployment_name}')
    subj_action = 'Update!'
    if latest_overall_version != curr_version:
        if latest_overall_version == latest_updatable_version:
            msg_action = f'Updated image to latest overall version, {latest_overall_version}'
            log_id = 'update_to_latest_overall_version'
        elif Version(latest_updatable_version) < Version(curr_version):
            msg_action = f'Did not update image.'
            subj_action = 'No update!'
            log_id = 'no_update'
        else:
            msg_action = f'Updated image to latest updatable version, {latest_updatable_version}'
            log_id = 'update_to_latest_updatable_version'
    else:
        if get_latest_preference_environment_variable() == 'true':
            msg_action = 'Updated image, restarted deployment to get the latest version, as LATEST environment variable is set to true'
            log_id = 'update_to_latest_overall_version_with_latest_preference'
        else:
            msg_action = 'Did not update to latest version, as LATEST environment variable is set to false'
            subj_action = 'No update!'
            log_id = 'no_update_with_latest_preference'
    
    msg = msg_template.substitute(msg_action=msg_action)
    subject = subject_template.substitute(subj_action=subj_action)

    log(logs_registry_json_id, curr_img_id, log_id, subject, msg, 'info', use_tls)


########## src/kube/main_operator.py ##########

def on_create_log(spec:dict, logs_registry_json_id:str, curr_img_id:str, kwargs:dict) -> None:
    """ Logs the creation of the operator.

    Args:
        spec (dict): The spec of the operator.
        logs_registry_json_id (str): The id of the logs registry json.
        curr_img_id (str): The id of the current image.
        kwargs (dict): The kwargs of the operator.
    
    Returns:
        None
    """    
    subject = f'onCreate: kopf operator {kwargs["name"]}'
    message = f'Created operator with name {kwargs["name"]} in namespace {kwargs["namespace"]} and uid {kwargs["uid"]} \n \
        Responsible of checking versions of the deployment: \n \
            {spec["deployment"]}'
    log(logs_registry_json_id, curr_img_id, 'on_create', subject, message, 'info')


def on_resume_log(spec:dict, logs_registry_json_id:str, curr_img_id:str, kwargs:dict) -> None:
    """ Logs the creation of the operator.

    Args:
        spec (dict): The spec of the operator.
        logs_registry_json_id (str): The id of the logs registry json.
        curr_img_id (str): The id of the current image.
        kwargs (dict): The kwargs of the operator.
    
    Returns:
        None
    """    
    subject = f'onResume: kopf operator {kwargs["name"]}'
    message = f'Resumed operator with name {kwargs["name"]} in namespace {kwargs["namespace"]} and uid {kwargs["uid"]} \n \
        Responsible of checking versions of the deployment: \n \
        {spec["deployment"]}'
    log(logs_registry_json_id, curr_img_id, 'on_resume', subject, message, 'info')


def on_delete_log(spec:dict, logs_registry_json_id:str, curr_img_id:str, kwargs:dict) -> None:
    """ Logs the deletion of the operator.

    Args:
        spec (dict): The spec of the operator.
        logs_registry_json_id (str): The id of the logs registry json.
        curr_img_id (str): The id of the current image.
        kwargs (dict): The kwargs of the operator.
    
    Returns:
        None
    """    
    subject = f'onDelete: kopf operator {kwargs["name"]}'
    message = f'Deleted operator with name {kwargs["name"]} in namespace {kwargs["namespace"]} and uid {kwargs["uid"]} \n \
        Responsible of checking versions of the deployment: \n \
        {spec["deployment"]}'
    log(logs_registry_json_id, curr_img_id, 'on_delete', subject, message, 'info')


def on_update_log(spec:dict, logs_registry_json_id:str, curr_img_id:str, kwargs:dict) -> None:
    """ Logs the update of the operator.

    Args:
        spec (dict): The spec of the operator.
        logs_registry_json_id (str): The id of the logs registry json.
        curr_img_id (str): The id of the current image.
        kwargs (dict): The kwargs of the operator.
    
    Returns:
        None
    """    
    subject = f'onUpdate: kopf operator {kwargs["name"]}'
    message = f'Updated operator with name {kwargs["name"]} in namespace {kwargs["namespace"]} and uid {kwargs["uid"]} \n \
        Responsible of checking versions of the deployment: \n \
        {spec["deployment"]}'
    log(logs_registry_json_id, curr_img_id, 'on_update', subject, message, 'info')


########## src/kube/kubernetes_api.py ##########

def get_api_instance_failed(apiserver_url:str, error_message:str, logs_registry_json_id:str, curr_img_id:str) -> None:
    """ Logs the failure of getting the api instance.

    Args:
        apiserver_url (str): The url of the apiserver.
        error_message (str): The error message.
        logs_registry_json_id (str): The id of the logs registry json.
        curr_img_id (str): The id of the current image.
    
    Returns:
        None
    """     
    subject = 'API instance retrieval failed'
    message = f'API instance retrieval failed for apiserver {apiserver_url} \n \
        The error message is: \n \
        {error_message} \n'
    log(logs_registry_json_id, curr_img_id, 'get_api_instance_failed', subject, message, 'error')


def restart_deployment_failed(deployment_name:str, deployment_namespace:str, error_message:str, logs_registry_json_id:str, curr_img_id:str) -> None:
    """ Logs the failure of restarting the deployment.

    Args:
        deployment_name (str): The name of the deployment.
        deployment_namespace (str): The namespace of the deployment.
        error_message (str): The error message.
        logs_registry_json_id (str): The id of the logs registry json.
        curr_img_id (str): The id of the current image.
    
    Returns:
        None
    """     
    subject = 'Deployment restart failed'
    message = f'Deployment {deployment_name} in namespace {deployment_namespace} failed to restart to pull newer latest image. \n \
        The error message is: \n \
        {error_message} \n'
    log(logs_registry_json_id, curr_img_id, 'restart_deployment_failed', subject, message, 'error')


def update_deployment_failed(deployment_name:str, deployment_namespace:str, img_name:str, tag:str, error_message:str, logs_registry_json_id:str, curr_img_id:str) -> None:
    """ Logs the failure of updating the deployment by patching.

    Args:
        deployment_name (str): The name of the deployment.
        deployment_namespace (str): The namespace of the deployment.
        img_name (str): The name of the image.
        tag (str): The tag of the image it was going to be updated to.
        error_message (str): The error message.
        logs_registry_json_id (str): The id of the logs registry json.
        curr_img_id (str): The id of the current image.
    
    Returns:
        None
    """     
    subject = 'Deployment update failed'
    message = f'Deployment {deployment_name} in namespace {deployment_namespace} failed while patching to update to image {img_name}:{tag}. \n \
        The error message is: \n \
        {error_message} \n'
    log(logs_registry_json_id, curr_img_id, 'update_deployment_failed', subject, message, 'error')


def get_bearer_token_failed(name:str, namespace:str, error_message:str, logs_registry_json_id:str, curr_img_id:str) -> None:
    """ Logs an error notifying about the failure of getting the bearer token.

    Args:
        name (str): The name of the account.
        namespace (str): The namespace of the account.
        error_message (str): The error message.
        logs_registry_json_id (str): The id of the logs registry json.
        curr_img_id (str): The id of the current image.
    
    Returns:
        None
    """    
    subject = 'Bearer token extraction failed.'
    message = f'Bearer token extraction failed for account {name} in namespace {namespace} \n \
        The error message is: \n \
        {error_message} \n'
    log(logs_registry_json_id, curr_img_id, 'get_bearer_token_failed', subject, message, 'error')


########## src/utilities/internet_connection.py ##########

def no_internet_connection_available_warning(logs_registry_json_id:str, curr_img_id:str) -> None:
    """ Logs a warning that no internet connection is available.

    Args:
        logs_registry_json_id (str): The id of the logs registry json.
        curr_img_id (str): The id of the current image.

    Returns:
        None
    """    
    subject = f'No internet connection.'
    message = f'No internet connection available. This means that the following services won\'t be available: \n \
        - DockerHub images updates \n \
        - Email logging \
        - Telegram logging \n \
        Check your DNS, proxy settings and firewall rules.'
    log(logs_registry_json_id, curr_img_id, 'no_internet_connection_available_warning', subject, message, 'warning')


########## src/utilities/gitlab/api.py ##########

def gitlab_credentials_not_found(logs_registry_json_id:str, curr_img_id:str) -> None:
    """ Logs an error that the gitlab credentials were not found.

    Args:
        logs_registry_json_id (str): The id of the logs registry json.
        curr_img_id (str): The id of the current image.

    Returns:
        None
    """    
    subject = f'Gitlab credentials not found.'
    message = f'Gitlab credentials not found. This means that the following services won\'t be available: \n \
        - Gitlab API \n \
        Check your Gitlab credentials: \n \
            - GITLAB_BASE_URL \n \
            - GITLAB_TOKEN \n \
            - GITLAB_PROJECT_ID \n '
    log(logs_registry_json_id, curr_img_id, 'gitlab_credentials_not_found', subject, message, 'error')


def gitlab_image_not_found(img_name:str, logs_registry_json_id:str, curr_img_id:str) -> None:
    """ Logs an error that the image was not found.

    Args:
        img_name (str): The name of the image.
        logs_registry_json_id (str): The id of the logs registry json.
        curr_img_id (str): The id of the current image.
    
    Returns:
        None 
    """    
    subject = f'Gitlab image {img_name} not found.'
    message = f'Gitlab image {img_name} not found at project {getenv("GITLAB_PROJECT_ID")}.'
    log(logs_registry_json_id, curr_img_id, 'gitlab_image_not_found', subject, message, 'error')


def no_gitlab_access(logs_registry_json_id:str, curr_img_id:str) -> None:
    """ Logs a debug message that no gitlab access is available.
    
    Args:
        logs_registry_json_id (str): The id of the logs registry json.
        curr_img_id (str): The id of the current image.
    
    Returns:
        None
    """    
    subject = 'No access to Gitlab.'
    message = 'Gitlab credentials have not been provided.'
    log(logs_registry_json_id, curr_img_id, 'no_gitlab_access', subject, message, 'debug')


def gitlab_obj_creation_failed(error_message:str, logs_registry_json_id:str, curr_img_id:str) -> None:
    """ Logs an error that the gitlab object creation failed.

    Args:
        error_message (str): The error message.
        logs_registry_json_id (str): The id of the logs registry json.
        curr_img_id (str): The id of the current image.
    
    Returns:
        None
    """    
    subject = 'Gitlab object creation failed.'
    log(logs_registry_json_id, curr_img_id, 'gitlab_obj_creation_failed', subject, error_message, 'error')


def get_gitlab_project_failed(error_message:str, logs_registry_json_id:str, curr_img_id:str) -> None:
    """ Logs an error that the gitlab project could not be retrieved.

    Args:
        error_message (str): The error message.
        logs_registry_json_id (str): The id of the logs registry json.
        curr_img_id (str): The id of the current image.
    
    Returns:
        None
    """     
    subject = 'Gitlab project retrieval failed.'
    log(logs_registry_json_id, curr_img_id, 'get_gitlab_project_failed', subject, error_message, 'error')


########## src/docker/dockerhub_api.py ##########

def get_updatable_docker_imgs_failed(img_name:str, img_namespace:str, version:str, url:str, page:str, logs_registry_json_id:str, curr_img_id:str) -> None:
    """ Logs an error that the updatable docker images could not be retrieved.

    Args:
        img_name (str): The name of the image.
        img_namespace (str): The namespace of the image.
        version (str): The version of the image.
        url (str): The url of the image.
        page (str): The page of the URL.
        logs_registry_json_id (str): The id of the logs registry json.
        curr_img_id (str): The id of the current image.
    
    Returns:
        None 
    """    
    subject = f'DockerHub traversing failed with image {img_name}:{version}.'
    message = f'DockerHub image {img_name}:{version} with namespace {img_namespace} at {url} page {page} presents some irregularity on the JSON response. \n \
        Check the mentioned url for debugging.'
    log(logs_registry_json_id, curr_img_id, 'get_updatable_docker_imgs_failed', subject, message, 'error')


def docker_date_not_found(img_name:str, tag:str, namespace:str, logs_registry_json_id:str, curr_img_id:str) -> None:
    """ Logs an error that the date of the image could not be found.

    Args:
        img_name (str): The name of the image.
        tag (str): The tag of the image.
        namespace (str): The namespace of the image.
        logs_registry_json_id (str): The id of the logs registry json.
        curr_img_id (str): The id of the current image.
    
    Returns:
        None
    """    
    subject = f'DockerHub image {img_name}:{tag} date not found.'
    message = f'DockerHub image {img_name}:{tag} with namespace {namespace} date not found.'
    log(logs_registry_json_id, curr_img_id, 'docker_date_not_found', subject, message, 'error')


def docker_image_not_found(img_name:str, logs_registry_json_id:str, curr_img_id:str) -> None:
    """ Logs an error that the image was not found.

    Args:
        img_name (str): The name of the image.
        logs_registry_json_id (str): The id of the logs registry json.
        curr_img_id (str): The id of the current image.
    
    Returns:
        None 
    """    
    subject = f'DockerHub image {img_name} not found.'
    message = f'While searching for the Docker image\'s {img_name} namespace at DockerHub, it was not found.'
    log(logs_registry_json_id, curr_img_id, 'docker_image_not_found', subject, message, 'error')
