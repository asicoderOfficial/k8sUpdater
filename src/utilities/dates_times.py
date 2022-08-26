from datetime import datetime
import re


def _datetime_matches_regex(regex:str, datetime_str:str) -> bool:
    """ Check if a string matches a regex.

    Args:
        regex (str): Regex to check.
        datetime_str (str): String to check.

    Returns:
        bool: True if the string matches the regex, False otherwise.
    """

    return re.match(regex, datetime_str) is not None


def docker_str_to_datetime(dt:str) -> datetime:
    """ Convert a string containing a dt in the format given by DockerHub, usually the last_updated field.
    An example of a dt is: 2022-06-15T13:14:25.654498Z

    Args:
        dt (str): String containing the datetime in the format given by DockerHub.

    Raises:
        ValueError: If the string does not match the expected format.

    Returns:
        datetime: dt in datetime format.
    """    
    docker_datetime_regex = '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?([zZ]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)?'
    if _datetime_matches_regex(docker_datetime_regex, dt):
        return datetime.strptime(dt.split('.')[0], '%Y-%m-%dT%H:%M:%S')
    else: 
        raise ValueError(f'Invalid dt format for date {dt} (expected a datetime string with the format given by DockerHub, see the example -> 2022-06-15T13:14:25.654498Z')
