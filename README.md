
# ![alt text](k8sUpdater_logo.png) K8sUpdater: Kubernetes automatic image versions control
![alt text](https://img.shields.io/badge/Python-3.8-blue)![alt text](https://img.shields.io/badge/license-Apache%202.0-blueviolet)

**K8sUpdater** is a Kubernetes operator that checks for updates of deployment's images available [DockerHub](https://hub.docker.com/search?q=) and [Gitlab](https://docs.gitlab.com/ee/user/packages/container_registry/) container registries, and updates automatically or notifies the user based on its preferences.

It is coded in Python 3.8 and uses the [Kopf](https://github.com/nolar/kopf) library to create the operator.

It was originally developed by [Asier Serrano Aramburu](https://www.linkedin.com/in/asierserrano/) during his 2022 [summer internship](https://home.cern/summer-student-programme) at [CERN](https://home.web.cern.ch/).

## Index
1. [How to use](https://github.com/asicoderOfficial/k8sUpdater#howtouse)
2. [Environment variables explanation](https://github.com/asicoderOfficial/k8sUpdater#environmentvariables)

    2.1. REFRESH_FREQUENCY_IN_SECONDS

    2.2. VERSIONS_FRONTIER

    2.3. LATEST_PREFERENCE

    2.4. Gitlab credentials

    2.5. E-mail logging credentials

    2.6. Telegram logging credentials

    
3. [Source code overview (for developers)](https://github.com/asicoderOfficial/k8sUpdater#sourcecodeoverview)

    3.1. src/docker_imgs

    3.2. src/gitlab

    3.3. src/kube

    3.4. src/utilities
4. [Logging system](https://github.com/asicoderOfficial/k8sUpdater#loggingsystem)
5. [Future work](https://github.com/asicoderOfficial/k8sUpdater#futurework)
6. [How to contribute](https://github.com/asicoderOfficial/k8sUpdater#howtocontribute)
7. [Buy me a coffee!](https://github.com/asicoderOfficial/k8sUpdater#buymeacoffee)
8. [License](https://github.com/asicoderOfficial/k8sUpdater/#license)

## 1. How to use

**IMPORTANT**: This operator will only work if the deployments it is checking the images of, have an ImagePullPolicy Always set!
The workflow is the following:
1. A cluster. You can create one easily with [Minikube](https://minikube.sigs.k8s.io/docs/start/).
2. Create and apply a [CustomResourceDefinition](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/).
3. Create and apply a deployment of [the image](https://hub.docker.com/repository/docker/asiertest/test-imgs).
4. Create and apply an [object](https://kubernetes.io/docs/concepts/overview/working-with-objects/kubernetes-objects/)
5. Optional: [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) and [ServiceAccount](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/) configuration.

Note: GitLab images tags must follow [PEP440](https://peps.python.org/pep-0440/) standard from the beginning, while in DockerHub the version numbers can be extracted from a non PEP440 as a substring, and then parsed.

Let's see it with an example! We'll create an operator that monitors a  <em>nginx</em> deployment, called nginx-deployment.

1. Apply the yamls/k8sUpdater-crd.yml file. Don't change anything of it. You will do this only once.
```yml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: versioninghandlers.k8supdater
spec:
  scope: Namespaced
  group: k8supdater
  names:
    kind: VersioningHandler
    plural: versioninghandlers
    singular: versioninghandler
    shortNames:
      - vh
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                deployment:
                  type: string
                containerregistry:
                  type: string
              required:
              - deployment
              - containerregistry
```
2. Configure and apply your deployment.yml file. There's a template at yamls/deployment.yml
```yml
apiVersion: apps/v1 
kind: Deployment
metadata:
  name: nginx-checker
spec:
  selector:
    matchLabels:
      app: nginx-checker
  template:
    metadata:
      labels:
        app: nginx-checker
    spec:
      containers:
      - name: k8sUpdater-nginx
        image: 
        imagePullPolicy: Always
        env:
          - name: REFRESH_FREQUENCY_IN_SECONDS
            value: "2"
          - name: VERSIONS_FRONTIER
            value: "2"
          - name: LATEST_PREFERENCE
            value: "true"
        ports:
        - containerPort: 80
    # DON'T FORGET TO SET COMPUTER POWER USAGE LIMITS!! -> https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
```
3. Create and apply the object. You can find the template at yamls/object.yml
```yml
apiVersion: k8supdater/v1
kind: VersioningHandler
metadata:
  name: nginx-checker
spec:
  deployment:
    'nginx-deployment'
  containerregistry:
    'dockerhub'
```

And that's it! Now the operator will be checking for suitable updates every 2 seconds.

For building your custom image, clone this repository, modify the code and build it using ```build.sh``` file.

## 2. Environment variables explanation
2.1. <em>REFRESH_FREQUENCY_IN_SECONDS</em>
**COMPULSORY**
It is used to indicate the amount of seconds between each check for new updates.
It is recommended to put a high value, such as 43200 (12 hours).

2.2. <em>VERSIONS_FRONTIER</em>
**COMPULSORY**
It denotes the limit between when to update automatically, and when to notify the user only.
* A newer versions is identified at the right of the frontier: update automatically, as it is not a major update that needs beforehand supervision.
* A newer versions is identified at the left of the frontier: notify the user, as it is a major update that needs beforehand supervision.

Let's illustrate it with some examples with a value of 2 (the frontier is denoted with a - ):
| Current version | Newer version at DockerHub | Action |
| --------------- | -------------------------- | ------ |
| 5.3. - 2.0      | 5.3. - 2.1                 | Update |
| 5.3. - 2.0      | 5.3. - 3.2                 | Update |
| 5.3. - 2.0      | 5.4. - 1                   | Notify |

It is important to note that, for DockerHub images, this will work also for the ones whose tag contains an operating system, such as 3.2.1-alpine.
It would find all the corresponding <em>-alpine</em> images, extract the version numbers and compare.

2.3. <em>LATEST_PREFERENCE</em>
**COMPULSORY**
There is a special case with latest tag.
If the current version is latest, and another latest is found to be newer, the user must specify if updating automatically or notifying. The possible values are the following:
* "true": Update automatically.
* "false": Notify that there's a newer latest.


2.4. Gitlab credentials.
Optional.
Only needed if a Gitlab container registry of a repository is needed to be tracked for a deployment.
* <em>GITLAB_BASE_URL</em>: The URL where all projects of your organization can be found.
* <em>GITLAB_TOKEN</em>: Personal access token, [see here](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html).
* <em>GITLAB_PROJECT_ID</em>: The numeric ID of the repository that contains the container registry.

2.5. E-mail logging credentials
Optional.
Required if the logs want to be sent by e-mail.
* <em>EMAIL_HOST</em>: The service that lets you send and receive e-mail across networks.
* <em>EMAIL_PASSWORD</em>: The password of sender.
* <em>EMAIL_SENDER</em>: Who sends the e-mail containing the log.
* <em>EMAIL_RECIPIENT</em>: Who receives the log e-mail.
* <em>EMAIL_PORT</em>: The port reserved for e-mail.

2.6. Telegram logging credentials
Optional.
Required if the logs want to be sent by Telegram. For doing so, you'll have to have a chat dedicated to this logging, by [creating a bot](https://core.telegram.org/Bots).
* <em>TELEGRAM_CHAT_ID</em>: The [id of the chat](https://telegram.me/myidbot).
* <em>TELEGRAM_TOKEN</em>: Authentication token.

## 3. Source code overview for developers
Brief overview of how the project's source code is structured.

3.1. ```src/docker_imgs```: Everything related to interacting with the DockerHub API.

3.2. ```src/gitlab```: Everything related to interacting with the GitLab API.

3.3. ```src/kube```: Where the operator code is located (```main_operator.py```) and everything related to interacting with the Kubernetes API.

3.4. ```src/utilities```: Multiple functionalities, such as logging, evironment variables handling, update function, versions checking and more.

## 4. Logging system
There are 3 channels for logging available, which share the same messages:
* Standard output: divides the messages in different categories, as in Python:
    * info
    * warning
    * debug
    * error
    * critical
* E-mail
* Telegram

There is one log message which indicates that nothing has changed. In order to not have this log repeated multiple times, a <em>non-spamming mechanism</em> has been developed.

For each object, a json file in a self-generated json folder is created, and inside it, the last log sent for each deployment's image is stored.

When sending a new log message, it is first checked that it is not the same as it was previously sent.

## 5. Future work
- [ ] Define a custom RegEx for parsing version names.
- [ ] Support more container registries.
- [ ] Set a delay between updates.
- [ ] Generate multiple replicas of the operator and share the workload between them.
- [ ] Enable multiple GitLab accounts in the same deployment.
- [ ] Implement GitHub Actions to automatically build and push the new image to DockerHub.
- [ ] Integration testing.

## 6. How to contribute
Check [this guide](https://gist.github.com/MarcDiethelm/7303312).

## 7. Buy me a coffee!

## 8. License
Apache 2.0 license.
