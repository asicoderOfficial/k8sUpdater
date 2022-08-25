import gitlab
from typing import Union
from src.utilities.environment_variables import _get_gitlab_environment_variables, _is_gitlab_ready
from src.utilities.logging_messages import gitlab_obj_creation_failed, get_gitlab_project_failed, gitlab_credentials_not_found
from traceback import format_exc


class GitlabProjectNotFoundException(Exception):
    """ Exception raised when the project is not found. """
    pass


class GitlabCanNotCreateObjectException(Exception):
    """ Exception raised when the object can not be created. """
    pass


class GitlabNoCredentialsFoundException(Exception):
    """ Exception raised when no credentials are found. """
    pass


def _create_gitlab_obj(base_url:str, token:str, logs_registry_json_id:str, curr_img_id:str) -> gitlab.Gitlab:
    """ Creates a Gitlab object.

    Args:
        base_url (str): The URL where all projects of your organization can be found.
        token (str): Private personal access token that gives access to the API.
        logs_registry_json_id (str): The ID of the logs registry JSON file.
        curr_img_id (str): The ID of the current image.

    Returns:
        gitlab.Gitlab: The Gitlab object.
    """    
    try:
        return gitlab.Gitlab(base_url, private_token=token)
    except Exception:
        gitlab_obj_creation_failed(format_exc(), logs_registry_json_id, curr_img_id)
        raise GitlabCanNotCreateObjectException(f'Can not create Gitlab object for base url {base_url} and given token.')


def _get_gitlab_project(gl:gitlab.Gitlab, project_id:str, logs_registry_json_id:str, curr_img_id:str):
    """ Returns the project with the given ID for the repository.

    Args:
        gl (gitlab.Gitlab): The Gitlab object.
        project_id (str): The ID of the project.
        logs_registry_json_id (str): The ID of the logs registry JSON file.
        curr_img_id (str): The ID of the current image.

    Returns:
        gitlab.v4.objects.projects.Project: The project object.
    """    
    try:
        return gl.projects.get(id=project_id)
    except Exception:
        get_gitlab_project_failed(format_exc(), logs_registry_json_id, curr_img_id)
        raise GitlabProjectNotFoundException(f'Can not find project with ID {project_id}.')


def get_all_gitlab_imgs_in_repository(logs_registry_json_id:str, curr_img_id:str, gl:gitlab.Gitlab=None) -> list:
    """ Get all images names contained in a repository container registry.

    Args:
        logs_registry_json_id (str): The ID of the logs registry JSON file.
        curr_img_id (str): The ID of the current image.
        gl (gitlab.Gitlab, optional): The Gitlab object. Defaults to None.

    Returns:
        list: List of images in the repository.
    """    
    if _is_gitlab_ready():
        base_url, token, project_id = _get_gitlab_environment_variables()
    else:
        gitlab_credentials_not_found(logs_registry_json_id, curr_img_id)
        raise GitlabNoCredentialsFoundException('No credentials found for Gitlab. Please specify them in the environment variables: \n \
                                                GITLAB_BASE_URL, GITLAB_BASE_TOKEN, GITLAB_PROJECT_ID')
    if base_url is None:
        return []
    if gl is None and base_url != token != project_id != '':
        # The method is being called externally, no gitlab object, credentials are directly used to create it.
        gl = _create_gitlab_obj(base_url, token, logs_registry_json_id, curr_img_id)
    project = _get_gitlab_project(gl, project_id, logs_registry_json_id, curr_img_id)
    plist = project.repositories.list(all=True)
    return [p.name for p in plist]
    

def get_gitlab_imgs_tags(image:str, logs_registry_json_id:str, curr_img_id:str) -> Union[dict, None]:
    """ For a specific project, extract all the images of the image registry, and return the tags sorted by the following logic:
    - The tag 'latest' has the bigger priority. If it exists, it will appear the first one.
    - The versions strings are sorted lexicographically.
    Finally, each array of tags will be sorted in descending order, thus placing the newest one in the first position.

    Args:
        image (str): Name of the image to extract tags for
        logs_registry_json_id (str): The ID of the logs registry JSON file.
        curr_img_id (str): The ID of the current image.

    Returns:
        dict: Sorted tags, in the format {image_name : [latest_tag, previous_to_latest_tag, ...]}
        None: No image is found, the exception is raised
    """    
    base_url, token, project_id = _get_gitlab_environment_variables()
    gl = _create_gitlab_obj(base_url, token, logs_registry_json_id, curr_img_id)
    project = _get_gitlab_project(gl, project_id, logs_registry_json_id, curr_img_id)
    plist = project.repositories.list(all=True)
    for p in plist:
        if p.name == image:
            return [tag.name for tag in p.tags.list()]
