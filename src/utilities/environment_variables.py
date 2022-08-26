from curses.ascii import isupper
from os import environ, getenv



def _is_email_logging_ready() -> bool:
    """ Check if email logging is ready.
    
    Returns:
        bool: True if email logging is ready, False otherwise.
    """    
    return 'EMAIL_HOST' in environ \
        and 'EMAIL_SENDER' in environ \
        and 'EMAIL_RECIPIENT' in environ \
        and 'EMAIL_PASSWORD' in environ \
        and 'EMAIL_PORT' in environ


def _get_email_environment_variables() -> tuple:
    """ Get email environment variables.
    Args:
        None
    
    Returns:
        tuple: The email environment variables.
    """
    return getenv('EMAIL_SENDER'), getenv('EMAIL_RECIPIENT'), getenv('EMAIL_PASSWORD'), getenv('EMAIL_HOST'), int(getenv('EMAIL_PORT'))


def _is_telegram_logging_ready() -> bool:
    """ Check if telegram logging is ready.
    
    Returns:
        bool: True if telegram logging is ready, False otherwise.
    """    
    return 'TELEGRAM_TOKEN' in environ \
        and 'TELEGRAM_CHAT_ID' in environ


def _get_telegram_environment_variables() -> tuple:
    """ Get telegram environment variables.
    Args:
        None
    
    Returns:
        tuple: The telegram environment variables.
    """    
    return getenv('TELEGRAM_TOKEN'), getenv('TELEGRAM_CHAT_ID')


def _is_gitlab_ready() -> bool:
    """ Check if gitlab is ready.
    
    Returns:
        bool: True if gitlab is ready, False otherwise.
    """    
    return 'GITLAB_BASE_URL' in environ \
        and 'GITLAB_TOKEN' in environ \
        and 'GITLAB_PROJECT_ID' in environ


def _get_gitlab_environment_variables() -> tuple:
    """ Get gitlab environment variables.
    Args:
        None
    
    Returns:
        tuple: The gitlab environment variables.
    """    
    return getenv('GITLAB_BASE_URL'), getenv('GITLAB_TOKEN'), getenv('GITLAB_PROJECT_ID')


def _name_env_variable(env_var_name:str) -> str:
    """ Given a property of the operator's CRD of the form firstwordSecondwordThirdword..., 
    insert an underscore before the capital letters and make it all uppercase.

    Args:
        env_var_name (str): The name of the environment variable, which starts with a lowercase letter and denotes the different words with a capital letter in the beginning.
        Examples of the format, what it means, returned name: versionsFrontier -> versions frontier -> VERSIONS_FRONTIER

    Returns:
        str: The environment variable name in the described format.
    """    
    return ''.join(('_' + ch if isupper(ch) else ch for ch in env_var_name)).upper()


def get_versions_frontier_environment_variable() -> int:
    """ Get the environment variable for the version frontier.
    
    Returns:
        int: The environment variable value for the version frontier.
    """    
    return int(getenv('VERSIONS_FRONTIER'))


def get_latest_preference_environment_variable() -> str:
    """ Get the environment variable for the latest preference.
    
    Returns:
        str: The environment variable value for the latest preference.
    """    
    return getenv('LATEST_PREFERENCE')


def get_refresh_frequency_in_seconds_environment_variable() -> int:
    """ Get the environment variable for the refresh frequency in seconds of the timer's decorator of main_operator.py file.
    
    Returns:
        int: The environment variable value for the refresh frequency in seconds.
    """    
    return int(getenv('REFRESH_FREQUENCY_IN_SECONDS'))


def get_internet_available_environment_variable() -> bool:
    """ Get the environment variable for the internet available.
    
    Returns:
        bool: The environment variable value for the internet available.
    """    
    return bool(getenv('INTERNET_AVAILABLE'))
