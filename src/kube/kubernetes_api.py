from datetime import datetime
from kubernetes import client, config
from traceback import format_exc
import base64
from src.utilities.environment_variables import get_latest_preference_environment_variable
from src.utilities.logging_messages import update_deployment_failed, restart_deployment_failed, get_bearer_token_failed, get_api_instance_failed
from traceback import format_exc



class CanNotGetBearerTokenException(Exception):
    """ Raised when the bearer token can not be obtained. """
    pass


class CanNotGetAPIInstanceException(Exception):
    """ Raised when the api instance can not be obtained. """
    pass


class CanNotUpdateDeploymentException(Exception):
    """ Raised when the deployment can not be updated. """
    pass


class CanNotRestartDeploymentException(Exception):
    """ Raised when the deployment can not be restarted. """
    pass


def get_kubernetes_api_instance() -> client.CoreV1Api:
    """ Obtains an api instance to interact with the kubernetes api from the main_operator.py file.

    Returns:
        client.CoreV1Api: The object with which we can interact with kubernetes api.
    """    
    try:
        # The operator is being executed in a pod (production).
        api_instance = client.CoreV1Api(config.load_incluster_config())
    except:
        # The operator is being executed from shell manually (development).
        api_instance = client.CoreV1Api(config.new_client_from_config())
        return api_instance
    return api_instance


def get_apiserver_url(api_instance:client.CoreV1Api) -> str:
    """ Obtains the apiserver url from the kubernetes api.

    Args:
        api_instance (client.CoreV1Api): The object with which we can interact with kubernetes api.

    Returns:
        str: The apiserver url, in format https://[host]:[port]
    """    
    # Get information for all pods
    resp = api_instance.list_pod_for_all_namespaces()
    # Set the URL needed to communicate with the API for updates beforehand
    for pod in resp.items:
        if 'kube-apiserver' in pod.metadata.name:
            for container in pod.spec.containers:
                if 'kube-apiserver' in container.image:
                    return f'https://{container.liveness_probe.http_get.host}:{container.liveness_probe.http_get.port}'


def get_namespaces_to_look_at(api_instance:client.CoreV1Api, native_namespaces:list=['kube-system', 'kube-node-lease', 'kube-public']) -> list:
    """ Get all namespaces except for the native ones, meaning that the deployments will be in them.

    Args:
        api_instance (client.CoreV1Api): The object with which we can interact with kubernetes api.
        native_namespaces (list, optional): The default namespaces which contain kubernetes native deployments. 
            Defaults to ['kube-system', 'kube-node-lease', 'kube-public'].

    Returns:
        list: The namespaces to look at.
    """    
    namespaces = api_instance.list_namespace()
    namespaces_to_look_at = []
    for namespace in namespaces.items:
        if namespace.metadata.name not in native_namespaces:
            namespaces_to_look_at.append(namespace.metadata.name)

    return namespaces_to_look_at


def update_container_image(img_name:str, deployment_name:str, deployment_namespace:str, apiserver_url:str, prev_tag:str, tag:str) -> None:
    """ Determines wether the image should be updated or not.

    Args:
        img_name (str): Name of the image of the deployment.
        deployment_name (str): Name of the deployment.
        deployment_namespace (str): Namespace of the deployment.
        apiserver_url (str): The configuration host and port, of the form https://[host]:[port]
        prev_tag (str): The previous tag the image had.
        tag (str): The tag user wants to update to. 
            If latest, the previous tag was latest, and the user wants to always be on latest, only a restart is needed.
            Else if the tag is not latest, the deployment body is changed, as an Always imagePullPolicy is assumed. 

    Returns:
        None
    """    
    api_instance = get_api_instance(apiserver_url)
    if tag == prev_tag == 'latest' and get_latest_preference_environment_variable() == 'true':
        restart_deployment(api_instance, deployment_name, deployment_namespace)
    elif tag != 'latest' and tag != prev_tag:
        update_img_version_in_deployment(api_instance, img_name, tag, deployment_name, deployment_namespace)


def get_bearer_token(api_instance:client.CoreV1Api, name:str, namespace:str) -> str:
    """ Obtain the bearer token to authenticate for using the kubernetes API.

    Args:
        api_instance (client.CoreV1Api): The object with which we can interact with kubernetes api.
        name (str): Name of the account.
        namespace (str): Namespace of the account.

    Returns:
        str: The bearer token, base64 decoded.
    """    
    try:
        # Get the service account resource
        sa_resource = api_instance.read_namespaced_service_account(name=name, namespace=namespace)
        # Get the token associated with the service account
        token_resource_name = [s for s in sa_resource.secrets if 'token' in s.name][0].name
        # Get the secret resource associated with the service account
        secret = api_instance.read_namespaced_secret(name=token_resource_name, namespace=namespace)
        # Get the token data out of the secret
        btoken = secret.data['token']
        # The token data is base64 encoded, so we decode it
        token = base64.b64decode(btoken).decode()
    except Exception:
        get_bearer_token_failed(name, namespace, format_exc())
        raise CanNotGetBearerTokenException(f'Could not get bearer token for account name {name} in namespace {namespace} from kubernetes api \n \
            {format_exc()}')

    return token


def get_api_instance(apiserver_url:str) -> client.AppsV1Api:
    """ Obtains an api instance to interact with the kubernetes api.

    Args:
        apiserver_url (str): The configuration host and port, of the form https://[host]:[port]

    Returns:
        client.AppsV1Api: The object with which we can interact with kubernetes api.
    """    
    try:
        configuration = client.Configuration()
        api_instance = client.CoreV1Api(config.new_client_from_config())
        configuration.host = apiserver_url
        configuration.api_key['authorization'] = get_bearer_token(api_instance, "default", "kube-system")
        configuration.api_key_prefix['authorization'] = 'Bearer'
        configuration.verify_ssl=False
        with client.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = client.AppsV1Api(api_client)
    except Exception:
        get_api_instance_failed(apiserver_url, format_exc())
        raise CanNotGetAPIInstanceException(f'Could not get api instance for apiserver url {apiserver_url} \n \
            {format_exc()}')

    return api_instance


def update_img_version_in_deployment(api_instance:client.CoreV1Api, img_name:str, tag:str, deployment_name:str, deployment_namespace:str) -> None:
    """ Updates the image version in the deployment by performing a patch, which changes the tag of the image.
    As an imagePullPolicy is assumed to be Always, the deployment is updated automatically.

    Args:
        api_instance (client.CoreV1Api): The object with which we can interact with kubernetes api.
        img_name (str): Name of the image of the deployment.
        tag (str): Tag to update to.
        deployment_name (str): Name of the deployment.
        deployment_namespace (str): Namespace of the deployment.

    Returns:
        None
    """    
    try:
        body = {
            'spec':{
                'template':{
                    'spec':{
                        'containers':[
                            {'name':img_name,
                            'image':f'{img_name}:{tag}'}
                            ]
                        }
                    }
                }
            }
        api_instance.patch_namespaced_deployment(deployment_name, deployment_namespace, body, pretty=True)
    except Exception:
        update_deployment_failed(deployment_name, deployment_namespace, img_name, tag, format_exc())
        raise CanNotUpdateDeploymentException(f'Could not update deployment {deployment_name} in namespace {deployment_namespace} with image {img_name}:{tag} \n \
            {format_exc()}')


def restart_deployment(api_instance:client.CoreV1Api, deployment_name:str, deployment_namespace:str) -> None:
    """ Restarts the given deployment. It is needed when the tag to update to, is the same (latest).
    Therefore, just a restart is needed, the tag does not change.

    Args:
        api_instance (client.CoreV1Api): The object with which we can interact with kubernetes api.
        deployment (str): Deployment name
        namespace (str): Deployment namespace
    
    Returns:
        None
    """
    try:
        now = datetime.utcnow()
        now = str(now.isoformat("T") + "Z")
        body = {
            'spec': {
                'template':{
                    'metadata': {
                        'annotations': {
                            'kubectl.kubernetes.io/restartedAt': now
                        }
                    }
                }
            }
        }
        api_instance.patch_namespaced_deployment(deployment_name, deployment_namespace, body, pretty='true')
    except Exception:
        restart_deployment_failed(deployment_name, deployment_namespace, format_exc())
        raise CanNotRestartDeploymentException(f'Could not restart deployment {deployment_name} in namespace {deployment_namespace} \n \
            {format_exc()}')
