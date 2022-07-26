from kubernetes import client, config
import base64
from datetime import datetime


def get_bearer_token(api_instance:client.CoreV1Api, name:str, namespace:str) -> str:
    """ Obtain the bearer token to authenticate for using the kubernetes API.

    Args:
        api_instance (client.CoreV1Api): The object with which we can interact with kubernetes api.
        name (str): Name of the account.
        namespace (str): Namespace of the account.

    Returns:
        str: The bearer token, base64 decoded.
    """    
    #Get the service account resource
    sa_resource = api_instance.read_namespaced_service_account(name=name, namespace=namespace)
    #Get the token associated with the service account
    token_resource_name = [s for s in sa_resource.secrets if 'token' in s.name][0].name
    #Get the secret resource associated with the service account
    secret = api_instance.read_namespaced_secret(
        name=token_resource_name, namespace=namespace)
    #Get the token data out of the secret
    btoken = secret.data['token']
    #The token data is base64 encoded, so we decode it
    token = base64.b64decode(btoken).decode()

    return token


#TODO: Add logging of api_response and return it in a human understandable way.
def update_container_image(img_name:str, deployment_name:str, deployment_namespace:str, apiserver_url:str, prev_tag:str, tag:str='latest') -> None:
    """ Determines wether the image should be updated or not.

    Args:
        img_name (str): Name of the image of the deployment.
        deployment_name (str): Name of the deployment.
        deployment_namespace (str): Namespace of the deployment.
        apiserver_url (str): The configuration host and port, of the form https://[host]:[port]
        prev_tag (str): The previous tag the image had.
        tag (str, optional): The tag user wants to update to. 
            If latest, and the previous tag was latest, only a restart is needed.
            Else, the deployment body is changed, as a Always imagePullPolicy is assumed. 
            Defaults to 'latest'.
    Returns:
        None
    """    
    configuration = client.Configuration()
    api_instance = client.CoreV1Api(config.new_client_from_config())
    configuration.host = apiserver_url
    configuration.api_key['authorization'] = get_bearer_token(api_instance, "default", "kube-system")
    configuration.api_key_prefix['authorization'] = 'Bearer'
    configuration.verify_ssl=False
    with client.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = client.AppsV1Api(api_client)
    if tag == prev_tag == 'latest':
        restart_deployment(api_instance, deployment_name, deployment_namespace)
    else:
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


def restart_deployment(api_instance:client.CoreV1Api, deployment:str, namespace:str) -> None:
    """ Restarts the given deployment. It is needed when the tag to update to, is the same (latest).

    Args:
        api_instance (client.CoreV1Api): The object with which we can interact with kubernetes api.
        deployment (str): Deployment name
        namespace (str): Deployment namespace
    
    Returns:
        None
    """
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
    api_instance.patch_namespaced_deployment(deployment, namespace, body, pretty='true')
