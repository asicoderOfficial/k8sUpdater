import requests
from json import loads
from urllib.request import urlopen
from src.utilities.urls import dockerhub_api_call_template_all_tags, dockerhub_cookies, dockerhub_search_api_call, dockerhub_api_call_template_specific_tag


class DockerHubImgNotFound(Exception):
    """ Raised when the image is not found on DockerHub.
    """    
    pass


def get_search_img_dockerhub_api(img_name:str) -> dict:
    """ Given an image name, this function queries the DockerHub API as if it was a user searching for that name on the webpage's Explore bar,
    to then get the namespace of it and be able to query the DockerHub API to get the dates of the latest and current versions.

    Args:
        img_name (str): The name of the image to search.

    Returns:
        json: The JSON response from the DockerHub API.
    """    
    return loads(requests.get(dockerhub_search_api_call.substitute(img_name=img_name), cookies=dockerhub_cookies).text)


def img_namespace_for_search_query(search_query_response:dict, img_name) -> str:
    """ Given a search query response from the DockerHub API, this function returns the namespace of the image.

    Args:
        search_query_response (dict): The JSON response from the DockerHub API.
        img_name (str): The name of the image to search.

    Raises:
        ValueError: If the response passed was already empty.
        DockerHubImgNotFound: If the response passed was not empty but did not contain the image name (there may be images that use it, but not the actual one).

    Returns:
        str: The namespace of the image.
    """    
    if search_query_response == {}: raise ValueError(f"No image found for {img_name}, the query passed was already empty.")
    for s in search_query_response['summaries']:
        if img_name in s['name']:
            namespace = 'library' if s['name'] == img_name else s['name'].split('/')[0]
            return namespace
    raise DockerHubImgNotFound(f'Image with name {img_name} not found in the DockerHub API response.')


def get_latest_img_date_dockerhub_api(namespace:str, name:str, tag:str) -> str:
    """ Given a namespace, name and tag of an image, this function queries the DockerHub API to get the date of the latest version of that image.

    Args:
        namespace (str): The namespace of the image.
        name (str): The name of the image.
        tag (str): The tag of the image.

    Returns:
        str: The date of the latest version of the image with the specified tag.
    """    
    return loads(urlopen(dockerhub_api_call_template_specific_tag.substitute(namespace=namespace, image_name=name, image_tag=tag)).read())['last_updated']


def get_version_for_latest_tag(img_name:str, img_namespace:str) -> str:
    """ Traverse the json that contains all the available versions of the image, to find the real version number corresponding to the latest tag.

    Args:
        img_name (str): The name of the image.
        img_namespace (str): The namespace of the image.

    Returns:
        str: The version of the image, which currently has the latest tag, e.g. 1.7.9
    """    
    catalog = loads(urlopen(dockerhub_api_call_template_all_tags.substitute(namespace=img_namespace, image_name=img_name)).read())
    for result in catalog['results']:
        if 'latest' in result['name']:
            latest_imgs_sha256 = set([img['digest'] for img in result['images']])
        else:
            curr_imgs_sha256 = set([img['digest'] for img in result['images']])
            if latest_imgs_sha256 == curr_imgs_sha256 and '.' in result['name']:
                return result['name']
