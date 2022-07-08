from kubernetes import client, config
import base64


def get_bearer_token(api_instance:client.CoreV1Api, name:str, namespace:str) -> str:
    # get the service account resource
    sa_resource = api_instance.read_namespaced_service_account(name=name, namespace=namespace)
    # get the token associated with the service account
    token_resource_name = [s for s in sa_resource.secrets if 'token' in s.name][0].name
    # get the secret resource associated with the service account
    secret = api_instance.read_namespaced_secret(
        name=token_resource_name, namespace=namespace)
    # get the token data out of the secret
    btoken = secret.data['token']
    # the token data is base64 encoded, so we decode it
    token = base64.b64decode(btoken).decode()

    return token


#TODO: Add logging of api_response and return it in a human understandable way.
def update_docker_image(img_name:str, deployment_name:str, deployment_namespace:str, apiserver_url:str, tag:str='latest') -> None:
    """ Determines wether the image should be updated or not.

    Args:
        img_name (str): Name of the image (without tag nor version).
        deployment_name (str): Deployment name.
        deployment_namespace (str): Deployment namespace.
        apiserver_url (str): URL with host_ip and host_port needed for connecting to the API server.
        tag (str, optional): Tag of the image to update to. Defaults to 'latest'.
    
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
    client.configuration.debug = True
    body = {'spec':{'template':{'spec':{'containers':[{'name':img_name,'image':f'{img_name}:{tag}'}]}}}}
    deployment_name = 'nginx-deployment'
    api_instance.patch_namespaced_deployment(deployment_name, deployment_namespace, body, pretty=True)
