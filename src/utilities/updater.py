from src.kube.kubernetes_api import update_container_image
from datetime import datetime
from src.utilities.logging_messages import updates_logs



def updating_engine(img_name:str, deployment_name:str, deployment_namespace:str, apiserver_url:str, prev_tag:str, \
    latest_updatable_version:str, latest_version_number:str, curr_img_date:datetime=None, latest_img_date:datetime=None) -> None:
    """ If needed, updates the image and logs the user accordingly.

    Args:
        img_name (str): Name of the image of the deployment.
        deployment_name (str): Name of the deployment.
        deployment_namespace (str): Namespace of the deployment.
        apiserver_url (str): The configuration host and port, of the form https://[host]:[port]
        prev_tag (str): The previous tag the image had.
        latest_version_number (str): The latest version number of the image.
        curr_img_date (datetime, optional): The datetime at which the current image was pushed to DockerHub. Defaults to None.
        latest_img_date (datetime, optional): The datetime at which the latest image was pushed to DockerHub. Defaults to None.

    Returns:
        None
    """    
    if (latest_updatable_version != '' and curr_img_date != None and latest_img_date != None and curr_img_date < latest_img_date and prev_tag == latest_updatable_version == 'latest') \
        or (prev_tag != latest_updatable_version != 'latest'):
        update_container_image(img_name, deployment_name, deployment_namespace, apiserver_url, prev_tag, latest_updatable_version)
        updates_logs(img_name, deployment_name, deployment_namespace, prev_tag, latest_updatable_version, latest_version_number)
    