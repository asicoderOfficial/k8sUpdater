from urllib.error import HTTPError
from urllib.request import urlopen
from src.utilities.logging_messages import no_internet_connection_available_warning
from os import environ, getenv



def is_there_internet_connection(logs_registry_json_id:str) -> bool:
    """ Checks if there is an internet connection.

    Args:
        logs_registry_json_id (str): The ID of the logs registry JSON file.

    Returns:
        bool: True if there is an internet connection, False otherwise.
    """    
    if 'INTERNET_AVAILABLE' in environ and getenv('INTERNET_AVAILABLE') == 'true':
        return True
    else:
        try:
            urlopen('https://www.google.com', timeout=1)
            environ['INTERNET_AVAILABLE'] = 'true'
            return True
        except HTTPError:
            no_internet_connection_available_warning(logs_registry_json_id, '')
            environ['INTERNET_AVAILABLE'] = 'false'
            return False
        except:
            environ['INTERNET_AVAILABLE'] = 'true'
            return True
