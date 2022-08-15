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


def _is_telegram_logging_ready() -> bool:
    """ Check if telegram logging is ready.
    
    Returns:
        bool: True if telegram logging is ready, False otherwise.
    """    
    return 'TELEGRAM_TOKEN' in environ \
        and 'TELEGRAM_CHAT_ID' in environ


def _get_email_environment_variables() -> tuple:
    """ Get email environment variables.
    Args:
        None
    
    Returns:
        tuple: The email environment variables.
    """
    return getenv('EMAIL_SENDER'), getenv('EMAIL_RECIPIENT'), getenv('EMAIL_PASSWORD'), getenv('EMAIL_HOST'), int(getenv('EMAIL_PORT'))


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


def set_environment_variables(env_vars:dict) -> None:
    """ Set the environment variables defined in env_vars for the current container.
    This method is meant to be used in development, to be able to easily change the environment variables with the object yaml file.

    Args:
        env_vars (dict): Contains the environment variables to be set, of the form {'environment_variable_name' : 'value'}.

    Returns:
        None
    """    
    for var_name, var_value in env_vars.items():
        if isinstance(var_value, str):
            var_name = _name_env_variable(var_name)
            if var_value.isdigit():
                environ[var_name.upper()] = int(var_value)
            elif var_value.isdecimal():
                environ[var_name.upper()] = float(var_value)
            else:
                environ[var_name.upper()] = var_value
        elif isinstance(var_value, list) and len(var_value) != 0:
            if var_name == 'gitlabContainerRegistry':
                environ['GITLAB_BASE_URL'] = var_value[0]            
                environ['GITLAB_TOKEN'] = var_value[1]
                environ['GITLAB_PROJECT_ID'] = var_value[2]
            elif var_name == 'emailLogging':
                environ['EMAIL_HOST'] = var_value[0]
                environ['EMAIL_PASSWORD'] = var_value[1]
                environ['EMAIL_SENDER'] = var_value[2]
                environ['EMAIL_RECIPIENT'] = var_value[3]
                environ['EMAIL_PORT'] = var_value[4]
            elif var_name == 'telegramLogging':
                environ['TELEGRAM_TOKEN'] = var_value[0]
                environ['TELEGRAM_CHAT_ID'] = var_value[1]
