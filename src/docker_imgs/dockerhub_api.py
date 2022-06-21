from json import loads
from os import popen
from urllib.request import urlopen
from src.utilities.commands import search_dockerhub_command
from src.utilities.urls import dockerhub_api_call_template


def get_search_img_dockerhub_api(img_name:str) -> dict:
    """ Given an image name, this function queries the DockerHub API as if it was a user searching for that name on the webpage's Explore bar,
    to then get the namespace of it and be able to query the DockerHub API to get the dates of the latest and current versions.

    Args:
        img_name (str): The name of the image to search.

    Returns:
        json: The JSON response from the DockerHub API.
    """    
    loads(popen(search_dockerhub_command.substitute(img_name=img_name)).read())


def img_namespace_for_search_query(search_query_response:dict, img_name) -> str:
    """ Given a search query response from the DockerHub API, this function returns the namespace of the image.

    Args:
        search_query_response (dict): The JSON response from the DockerHub API.
        img_name (str): The name of the image to search.

    Raises:
        ValueError: If the response passed was already empty.
        Exception: If the response passed was not empty but did not contain the image name (there may be images that use it, but not the actual one).

    Returns:
        str: The namespace of the image.
    """    
    if search_query_response == {}: raise ValueError(f"No image found for {img_name}, the query passed was already empty.")
    for s in search_query_response['summaries']:
        if img_name in s['name']:
            namespace = 'library' if s['name'] == img_name else s['name'].split('/')[0]
            return namespace
    raise Exception(f'Image with name {img_name} not found in the DockerHub API response.')


def get_latest_img_date_dockerhub_api(namespace:str, name:str, tag:str) -> str:
    """ Given a namespace, name and tag of an image, this function queries the DockerHub API to get the date of the latest version of that image.

    Args:
        namespace (str): The namespace of the image.
        name (str): The name of the image.
        tag (str): The tag of the image.

    Returns:
        str: The date of the latest version of the image with the specified tag.
    """    
    return loads(urlopen(dockerhub_api_call_template.substitute(namespace=namespace, image_name=name, image_tag=tag)).read())['last_updated']