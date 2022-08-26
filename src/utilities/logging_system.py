from os import mkdir
from os.path import exists
from json import load, dumps
from email.message import EmailMessage
from traceback import format_exc
from smtplib import SMTP, SMTP_SSL
import requests
from logging import Handler, Formatter
import datetime
import logging
from os import getenv
from src.utilities.environment_variables import _is_email_logging_ready, _is_telegram_logging_ready, _get_email_environment_variables, _get_telegram_environment_variables, get_internet_available_environment_variable



def log(logs_registry_json_id:str, curr_img_id:str, log_id:str, subject:str, message:str, level:str, use_tls:bool=False) -> None:
    """ Main logging function, responsible of redirecting message and subject to the different available logging systems.

    Args:
        logs_registry_json_id (str): The id of the json file where the logs registry is stored.
        curr_img_id (str): The id of the current image.
        log_id (str): The id of the log.
        subject (str): The subject of the message.
        message (str): The message to be posted.
        level (str): The level of the message, important for the standard output logging.
        logs_registry_json_id (str): The id of the json file where the logs registry is stored.
        use_tls (bool, optional): If using TLS for securing emails. Defaults to False.
    
    Returns:
        None
    """    
    if _is_log_not_repeated(logs_registry_json_id, log_id, curr_img_id):
        _update_last_log_registry(logs_registry_json_id, curr_img_id, log_id)
        stdout_logging(subject, message, level=level)
        email_logging(curr_img_id, logs_registry_json_id, subject, message, use_tls=use_tls)
        telegram_logging(curr_img_id, logs_registry_json_id, subject, message)


def _is_log_not_repeated(logs_registry_json_id:str, log_id:str, curr_img_id:str) -> bool:
    """ Check if the log has already been posted.

    Args:
        logs_registry_json_id (str): The id of the json file where the logs registry is stored.
        log_id (str): The id of the log.
        curr_img_id (str): The id of the image that is being checked for updates.

    Returns:
        bool: True if the log has not been posted, False otherwise.
    """    
    _create_log_registry_file_if_needed(logs_registry_json_id)
    last_log_registry = _read_last_log_registry(logs_registry_json_id)
    if curr_img_id not in last_log_registry:
        _update_last_log_registry(logs_registry_json_id, curr_img_id, log_id)
        return True
    else:
        return True if log_id != last_log_registry[curr_img_id] else False


def _create_log_registry_file_if_needed(logs_registry_id:str) -> None:
    """ Create the log registry file if it does not exist.
    This registry is stored in a hidden json under a created json folder.
    
    Args:
        logs_registry_id (str): The id of the logs registry json file for the current operator.
    
    Returns:
        None
    """    
    if not exists('json'):
        mkdir('json')
    if not exists(f'json/{logs_registry_id}.json'):
        with open(f'json/{logs_registry_id}.json', 'w') as f:
            f.write(dumps({}))


def _read_last_log_registry(logs_registry_id:str) -> dict:
    """ Get the last log registry.
    This registry is stored in a hidden json under a created json folder.
    
    Args:
        logs_registry_id (str): The id of the logs registry json file for the current operator.
    
    Returns:
        dict: The last log registry.
    """    
    with open(f'json/{logs_registry_id}.json', 'r') as f:
        return load(f)


def _overwrite_last_log_registry(logs_registry_id:str, last_log_registry:dict) -> None:
    """ Set the last log registry.
    This registry is stored in a hidden json under a created json folder.
    
    Args:
        logs_registry_id (str): The id of the logs registry json file for the current operator.
    
    Returns:
        None
    """    
    #Overwrite last_log_registry in json file
    with open(f'json/{logs_registry_id}.json', 'w') as f:
        f.write(dumps(last_log_registry))


def _update_last_log_registry(logs_registry_id:str, curr_img_id:str, last_log:str) -> None:
    """ Update the last log registry.
    This registry is stored in a hidden json under a created json folder.

    Args:
        logs_registry_id (str): The id of the logs registry json file for the current operator.
        curr_img_id (str): The current image id.
        last_log (str, optional): The id of the last log. Defaults to ''.
    
    Returns:
        None
    """    
    last_log_registry = _read_last_log_registry(logs_registry_id)
    last_log_registry[curr_img_id] = last_log
    _overwrite_last_log_registry(logs_registry_id, last_log_registry)


def email_logging(curr_img_id:str, logs_registry_json_id:str, subject:str, message:str, use_tls:bool=False) -> None:
    """ Log through email.

    Args:
        curr_img_id (str): The id of the current image.
        logs_registry_json_id (str): The id of the json file where the logs registry is stored.
        subject (str): Subject of the email. Should be short and concise.
        message (str): Body of the email.
        use_tls (bool, optional): Defines if TLS handshake is required or not. Defaults to False.
    
    Returns:
        None
    """    
    if get_internet_available_environment_variable() == 'true' and _is_email_logging_ready():
        try:
            sender, recipient, password, host, port = _get_email_environment_variables()

            # Create your SMTP session 
            if password == '':
                smtp_server = SMTP(host, port) 
            else:
                smtp_server = SMTP_SSL(host, port)
            if use_tls:
                # Use TLS to add security 
                smtp_server.starttls() 
            # Defining The Message 
            email_obj = EmailMessage()
            email_obj.set_content(message)
            email_obj['Subject'] = subject
            email_obj['From'] = sender
            email_obj['To'] = recipient

            # Sending the Email
            smtp_server.login(sender, password)
            smtp_server.send_message(email_obj)
            # Terminating the session 
            smtp_server.quit()
        except Exception:
            subject = 'Email logging failed'
            message = f'{format_exc()} \n \
                Review your email environment variables of the deployment, which currently have the following values: \n \
                    EMAIL_HOST: {getenv("EMAIL_HOST")} \n \
                    EMAIL_SENDER: {getenv("EMAIL_SENDER")} \n \
                    EMAIL_RECIPIENT: {getenv("EMAIL_RECIPIENT")} \n \
                    EMAIL_PORT: {getenv("EMAIL_PORT")} \n \
                    Check also your EMAIL_PASSWORD value. \n'
            if _is_log_not_repeated(logs_registry_json_id, 'email_logging_failed', curr_img_id):
                stdout_logging(subject, message, level='error')


def telegram_logging(curr_img_id:str, logs_registry_json_id:str, subject:str, message:str) -> None:
    """ Log through Telegram.
    Args:
        curr_img_id (str): The id of the current image.
        logs_registry_json_id (str): The id of the json file where the logs registry is stored.
        subject (str): The subject of the message.
        message (str): The message to be posted.
    
    Returns:
        None
    """
    if get_internet_available_environment_variable() == 'true' and _is_telegram_logging_ready():
        try:
            token, chat_id = _get_telegram_environment_variables()
            TelegramLog(token, chat_id).send(subject, message)
        except Exception:
            subject ='Telegram logging failed' 
            message = f'{format_exc()} \n \
                Review your telegram environment variables of the deployment, which currently have the following values: \n \
                    TELEGRAM_CHAT_ID: {getenv("TELEGRAM_CHAT_ID")} \n \
                    Check also your TELEGRAM_TOKEN value. \n'
            if _is_log_not_repeated(logs_registry_json_id, 'email_logging_failed', curr_img_id):
                stdout_logging(subject, message, level='error')


def stdout_logging(subject:str, msg:str, level:str='info') -> None:
    """ Log through stdout.
    Args:
        subject (str): The subject of the message.
        msg (str): The message to be posted.
        level (str, optional): The level of the message. Defaults to 'info'.
    
    Returns:
        None
    """
    if level == 'info':
        logging.info(f'{subject}: \n {msg} \n')
    elif level == 'warning':
        logging.warning(f'{subject}: \n {msg} \n')
    elif level == 'debug':
        logging.debug(f'{subject}: \n {msg} \n')
    elif level == 'error':
        logging.error(f'{subject}: \n {msg} \n')
    else:
        logging.critical(f'{subject}: \n {msg} \n')


# Telegram logger class

class RequestsHandler(Handler):
    def __init__(self, token:str, chat_id:str):
        super().__init__()
        self.token = token
        self.chat_id = chat_id

    def emit(self, record:str) -> str:
        """ Post a message to the Telegram chat.
        Args:
            record (str): The message to be posted.
        Returns:
            str: The message posted. 
        """        
        log_entry = self.format(record)
        payload = {
        'chat_id': self.chat_id,
        'text': log_entry,
        'parse_mode': 'HTML'
        }
        return requests.post("https://api.telegram.org/bot{token}/sendMessage".format(token=self.token),
            data=payload).content


class LogstashFormatter(Formatter):
    def __init__(self) -> None:
        super(LogstashFormatter, self).__init__()

    def format(self, record):
        t = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        return "<i>{datetime}</i><pre>\n{message}</pre>".format(message=record.msg, datetime=t)


class TelegramLog():
    def __init__(self, token:str, chat_id:str, logger_name:str='default') -> None:
        self.token = token
        self.chat_id = chat_id
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.ERROR)
        self.handler = RequestsHandler(self.token, self.chat_id)
        self.formatter = LogstashFormatter()
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.WARNING)
    
    def send(self, message:str) -> None:
        """ Send a message to the Telegram chat.
        Args:
            message (str): The message to be posted.
        Raises:
            ValueError: The given message is not of type str.
        """
        if not isinstance(message, str): raise TypeError('"message" must be of type str.')
        self.logger.error(message)
