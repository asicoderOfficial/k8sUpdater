import gitlab
from packaging import version
from os import getenv
from typing import Union


def get_gitlab_imgs_tags(base_url:str, token:str, project_id:str, image:str) -> Union[dict, None]:
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

    Raises:
        ValueError: The specified image, does not exist in the repository.

    Returns:
        dict: Sorted tags, in the format {image_name : [latest_tag, previous_to_latest_tag, ...]}
        None: No image is found, the exception is raised
    """    
    gl = gitlab.Gitlab(base_url, private_token=token)
    project = gl.projects.get(id=project_id)
    plist = project.repositories.list(all=True)
    for p in plist:
        if p.name == image:
            return [tag.name for tag in p.tags.list()]
    raise ValueError(f'No image named {image} is present at the repository')


def get_latest_tag_for_image(image:str) -> str:
    """ Extracts the latest tag available for the specified image.
    It gives priority to the tag latest, if found.

    Args:
        image (str): The name of the image.

    Returns:
        str: The latest tag.
    """    
    img_tags = get_gitlab_imgs_tags(getenv('GITLAB_BASE_URL'), getenv('GITLAB_TOKEN'), getenv('PROJECT_ID'), image)
    for idx, tag in enumerate(img_tags):
        if tag == 'latest':
            return 'latest'
        img_tags[idx] = version.parse(tag)

    return str(max(img_tags))
        