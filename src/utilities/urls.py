import re
from string import Template


dockerhub_api_call_template = Template('https://hub.docker.com/v2/repositories/$namespace/$image_name/tags/$image_tag')


def _container_id_is_docker(container_id:str) -> bool:
    """ Check if the containerID field resulting from kubectl, matches the regex that determines if it is a docker container.
    An example of containerID could be: docker://5cff15d6baccdb401ea1b1b1cb1b24b113f13c4a1e06df268f1233fda4655c10
    This is important next, check accordingly the date of the desired image tag.

    Args:
        container_id (str): Container ID to check.

    Returns:
        bool: True if the string is a Docker container ID (matches the regex), False otherwise.
    """

    return re.match('docker-pullable://[a-zA-Z]+@sha256:([a-zA-Z]+([0-9]+[a-zA-Z]+)+)', container_id) is not None
