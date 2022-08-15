import gitlab
from typing import Union
from src.utilities.environment_variables import _get_gitlab_environment_variables
from src.utilities.logging_messages import gitlab_obj_creation_failed, get_gitlab_project_failed
from traceback import format_exc


class GitlabProjectNotFoundException(Exception):
    """ Exception raised when the project is not found. """
    pass


class GitlabCanNotCreateObjectException(Exception):
    """ Exception raised when the object can not be created. """
    pass


def _create_gitlab_obj(base_url:str, token:str) -> gitlab.Gitlab:
    """ Creates a Gitlab object.

    Args:
        base_url (str): The URL where all projects of your organization can be found.
        token (str): Private personal access token that gives access to the API.

    Returns:
        gitlab.Gitlab: The Gitlab object.
    """    
    try:
        return gitlab.Gitlab(base_url, private_token=token)
    except Exception:
        gitlab_obj_creation_failed(format_exc())
        raise GitlabCanNotCreateObjectException(f'Can not create Gitlab object for base url {base_url} and given token.')


def _get_gitlab_project(gl:gitlab.Gitlab, project_id:str):
    """ Returns the project with the given ID for the repository.

    Args:
        gl (gitlab.Gitlab): The Gitlab object.
        project_id (str): The ID of the project.

    Returns:
        gitlab.v4.objects.projects.Project: The project object.
    """    
    try:
        return gl.projects.get(id=project_id)
    except Exception:
        get_gitlab_project_failed(format_exc())
        raise GitlabProjectNotFoundException(f'Can not find project with ID {project_id}.')


def get_all_gitlab_imgs_in_repository(gl:gitlab.Gitlab=None) -> list:
    """ Get all images names contained in a repository container registry.

    Args:
        gl (gitlab.Gitlab, optional): The Gitlab object. Defaults to None.

    Returns:
        list: List of images in the repository.
    """    
    base_url, token, project_id = _get_gitlab_environment_variables()
    if base_url is None:
        return []
    if gl is None and base_url != token != project_id != '':
        #The method is being called externally, no gitlab object, credentials are directly used to create it.
        gl = _create_gitlab_obj(base_url, token)
    project = _get_gitlab_project(gl, project_id)
    plist = project.repositories.list(all=True)
    return [p.name for p in plist]
    

def get_gitlab_imgs_tags(image:str) -> Union[dict, None]:
    """ For a specific project, extract all the images of the image registry, and return the tags sorted by the following logic:
    - The tag 'latest' has the bigger priority. If it exists, it will appear the first one.
    - The versions strings are sorted lexicographically.
    Finally, each array of tags will be sorted in descending order, thus placing the newest one in the first position.

    Args:
        base_url (str): The URL where all projects of your organization can be found.
                        See here -> https://docs.gitlab.com/ee/user/project/pages/getting_started_part_one.html
        token (str): Private personal access token that gives access to the API.
                     It can be generated as explained here -> https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html
        project_id (str): ID of the project accessible by the authenticated user.
                          It can be found at the repository main page in Gitlab.
        image (str): Name of the image to extract tags for.

    Returns:
        dict: Sorted tags, in the format {image_name : [latest_tag, previous_to_latest_tag, ...]}
        None: No image is found, the exception is raised
    """    
    base_url, token, project_id = _get_gitlab_environment_variables()
    gl = _create_gitlab_obj(base_url, token)
    project = _get_gitlab_project(gl, project_id)
    plist = project.repositories.list(all=True)
    for p in plist:
        if p.name == image:
            return [tag.name for tag in p.tags.list()]
