from urllib.error import HTTPError
from urllib.request import urlopen
from src.utilities.logging_messages import no_internet_connection_available_warning
from os import environ, getenv



def is_there_internet_connection() -> bool:
    """ Checks if there is an internet connection.

    Returns:
        bool: True if there is an internet connection, False otherwise.
    """    
    if 'INTERNET_AVAILABLE' in environ and getenv('INTERNET_AVAILABLE') == 'true':
        return True
    else:
        try:
            urlopen('http://www.google.com', timeout=1)
            environ['INTERNET_AVAILABLE'] = 'true'
            return True
        except HTTPError:
            no_internet_connection_available_warning()
            environ['INTERNET_AVAILABLE'] = 'false'
            return False
