import re
from packaging import version
import requests
from json import loads
from urllib.request import urlopen
from src.utilities.urls import dockerhub_api_call_template_all_tags, dockerhub_headers, dockerhub_search_api_call, dockerhub_api_call_template_specific_tag
from src.utilities.logging_messages import get_updatable_docker_imgs_failed, docker_image_not_found, docker_date_not_found
from urllib.error import HTTPError


class DockerHubImgNotFound(Exception):
    """ Raised when the image is not found on DockerHub.
    """    
    pass


class DockerHubDateNotFound(Exception):
    """ Raised when the date of a version of an image is not found on DockerHub.
    """    
    pass


class DockerHubAbnormalJSONResponse(Exception):
    """ Raised when the JSON response from the DockerHub API is abnormal.
    """    
    pass


def get_search_img_dockerhub_api(img_name:str, logs_registry_json_id:str, curr_img_id:str) -> dict:
    """ Given an image name, this function queries the DockerHub API as if it was a user searching for that name on the webpage's Explore bar,
    to then get the namespace of it and be able to query the DockerHub API to get the dates of the latest and current versions.

    Args:
        img_name (str): The name of the image to search.
        logs_registry_json_id (str): The ID of the logs registry JSON file.
        curr_img_id (str): The ID of the current image.

    Returns:
        json: The JSON response from the DockerHub API.
    """    
    try:
        return loads(requests.get(dockerhub_search_api_call.substitute(img_name=img_name), cookies=dockerhub_headers, timeout=0.4).text)
    except Exception:
        docker_image_not_found(img_name, logs_registry_json_id, curr_img_id)
        raise DockerHubImgNotFound(f'Image with name {img_name} not found in the DockerHub API response while looking for its corresponding namespace.')
    

def img_namespace_for_search_query(search_query_response:dict, img_name:str, logs_registry_json_id:str, curr_img_id:str) -> str:
    """ Given a search query response from the DockerHub API, this function returns the namespace of the image.

    Args:
        search_query_response (dict): The JSON response from the DockerHub API.
        img_name (str): The name of the image to search.
        logs_registry_json_id (str): The ID of the logs registry JSON file.
        curr_img_id (str): The ID of the current image.

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
    docker_image_not_found(img_name, logs_registry_json_id, curr_img_id)
    raise DockerHubImgNotFound(f'Image with name {img_name} not found in the DockerHub API response while looking for its corresponding namespace.')


def get_latest_img_date_dockerhub_api(img_namespace:str, img_name:str, img_tag:str, logs_registry_json_id:str, curr_img_id:str) -> str:
    """ Given a namespace, name and tag of an image, this function queries the DockerHub API to get the date of the latest version of that image.

    Args:
        img_namespace (str): The namespace of the image.
        img_name (str): The name of the image.
        img_tag (str): The tag of the image.
        logs_registry_json_id (str): The ID of the logs registry JSON file.
        curr_img_id (str): The ID of the current image.

    Returns:
        str: The date of the latest version of the image with the specified tag.
    """    
    try:
        return loads(urlopen(dockerhub_api_call_template_specific_tag.substitute(namespace=img_namespace, image_name=img_name, image_tag=img_tag)).read())['last_updated']
    except Exception:
        docker_date_not_found(img_name, img_tag, img_namespace, logs_registry_json_id, curr_img_id)
        raise DockerHubDateNotFound(f'Date of the latest version of the image {img_namespace}/{img_name}:{img_tag} not found in the DockerHub API response.')


def get_updatable_dockerhub_imgs(img_name:str, img_namespace:str, curr_version:str, logs_registry_json_id:str, curr_img_id:str) -> dict:
    """ Traverse the json that contains all the available versions of the image,
    saving all the newer versions of the image in a dictionary.

    That way, later, we can get the latest version of the image, 
    and the latest automatically updatable version, based on the version_frontier parameter specified by the user.

    Args:
        img_name (str): The name of the image.
        img_namespace (str): The namespace of the image.
        curr_version (str): The current name of the image.
        logs_registry_json_id (str): The ID of the logs registry JSON file.
        curr_img_id (str): The ID of the current image.

    Returns:
        dict: All images previous to the current version available in DockerHub.
            - keys: packaging.version.Version objects, representing the versions, following the regex '(\d\.?)+'
            - values: the corresponding tags, contained in 'name' field of the JSON response.
    """    
    newer_versions = {}

    sha256_of_found_imgs = set()
    page = 1
    reg = '(\d\.?)+'
    regexp = re.compile(reg)
    curr_version_regex_search = regexp.search(curr_version)
    if curr_version_regex_search is not None:
        # The version number of the deployment's image contains a PEP440 version number as a substring.
        curr_version_found = curr_version_regex_search.group()
        # Extract the version number, and the substrings before and after it.
        curr_version_partition = curr_version.partition(curr_version_found)
    else:
        # No PEP440 version number found in the deployment's image.
        return newer_versions
    try:
        url = dockerhub_api_call_template_all_tags.substitute(namespace=img_namespace, image_name=img_name, page=page)
        while True:
            content = loads(urlopen(url).read())
            for res in content['results']:
                m = regexp.search(res['name'])        
                if m is not None:
                    # The version number of DockerHub's registry contains a PEP440 version number as a substring.
                    version_number = m.group()
                    tag_partition = res['name'].partition(version_number)
                    if tag_partition[0] == curr_version_partition[0] \
                        and tag_partition[2] == curr_version_partition[2]:
                        if tag_partition[1] == curr_version_partition[1]:
                            return newer_versions
                        # As traversing is linear with time, the first version that is found is the latest version, and the last is the first one.
                        # However, there are versions that specify the latest of a level. That's why sha256 must be compared as well.
                        found_version_obj = version.Version(version_number)
                        if 'digest' in res \
                        and res['digest'] not in sha256_of_found_imgs:
                            sha256_of_found_imgs.add(res['digest'])
                            newer_versions[found_version_obj] = res['name']
                        elif 'digest' not in res:
                            newer_versions[found_version_obj] = res['name']
            page += 1 
    except HTTPError:
        # No match is found, or all matches found are newer than the current version.
        return newer_versions
    except Exception:
        get_updatable_docker_imgs_failed(img_name, img_namespace, curr_version, url, page, logs_registry_json_id, curr_img_id)
        raise DockerHubAbnormalJSONResponse(f'Abnormal response from the DockerHub API while getting the updatable images for the image {img_name} of namespace {img_namespace}.')
    

def get_latest_version_dockerhub(available_newer_imgs:dict) -> str:
    """ Given a dictionary containing all the newer versions of the image, this function returns the latest version of the image.
    The latest version is the one with the highest version number.

    Args:
        available_newer_imgs (dict): All images previous to the current version available in DockerHub.
    
    Returns:
        str: The latest version of the image.
    """
    return str(max(available_newer_imgs.keys())) if available_newer_imgs else ''
