from packaging.version import Version, InvalidVersion



def perform_automatic_update(curr_version_number:str, latest_version_number:str, version_frontier:int) -> bool:
    """ Based on the user's specified latest_version_number, perform an update automatically, or not.
    The algorithm to check for updates is the following:
    1. Split the version numbers by dots, obtaining a list of the numbers in the original order.
    2. Base case: the version frontier is = 0 or  len(curr_version_number_levels) - Indicates update always.
    3. Get the shortest list (version number with less dots).
    4. Traverse from 0 to version_frontier-2, to check the latest surpasses current in the region the levels the user wants to avoid for automatic updates.
    If it outdated - DO NOT UPDATE.
    5. Traverse from version_frontier-1 to the end of the shortest list. If it is outdated - UPDATE.
    6. If no outdated version has been found while traversing, and the shortest version number turns out to be the current,
    it means that there are new smaller updates - UPDATE.
    7. Else, DO NOT UPDATE, only notify, as the update may be bigger than expected

    Args:
        curr_version_number (str): Version number of the current image.
        latest_version_number (str): Version number of the latest image.
        version_frontier (int): The number that divides the update automatically/notify areas.
            A user may not want to automatically make big updates, as it may break production code with deprecations for instance.
            However, doing minor controlled updates without much supervision is recommended, as it improves security.
            Therefore, this variable defines a barrier. For example:
            -version_frontier = 2, curr_version_frontier=3.5.2.1, latest_version_number=4.6.2.2 - 3.5|.2.1 & 4.6|.2.2 respectively.

    Returns:
        bool: Update automatically or not, True or False respectively.
    """    
    if curr_version_number == 'latest' and latest_version_number == 'latest': return True
    latest_version_levels = latest_version_number.split('.')
    curr_version_levels = curr_version_number.split('.')
    shortest_version_number = min(len(latest_version_levels), len(curr_version_levels))
    if version_frontier <= 0 or version_frontier > shortest_version_number:
        return True
    elif curr_version_number == latest_version_number:
        return False
    # Check if before the frontier, the versions are the same.
    for i in range(version_frontier):
        if latest_version_levels[i] > curr_version_levels[i]:
            return False
    # Check if after the frontier, the current version is outdated.
    for i in range(version_frontier, shortest_version_number):
        if latest_version_levels[i] > curr_version_levels[i]:
            return True
    if shortest_version_number == len(curr_version_levels):
        # Before and after the frontier the version is the same, and the shortest version number is the current:
        # there are newer versions with a higher level of granularity.
        return True
    return False


def get_latest_version(versions:list, filter:bool=False) -> str:
    """ Extracts the latest version available.
    It gives priority to the tag latest, if found.

    Args:
        versions (list): Versions available, represented as strings.

    Returns:
        str: The latest tag.
            If no latest version, or no PEP 440 style specified image is found, the empty string is returned.
    """    
    if 'latest' in versions:
        return 'latest'
    elif filter:
        versions = filter_pep404_versions(versions)['correct_format']
    for idx, tag in enumerate(versions):
        versions[idx] = Version(tag)

    return str(max(versions)) if versions != [] else ''
    

def get_latest_pep440_updatable_version(curr_version:str, img_versions:list, version_frontier:int) -> str:
    """ Return the last version the user can update to, according to the version frontier specified.
    It may not be the latest available version.

    Args:
        curr_version (str): Current version of the image.
        img_versions (list): Versions of the image available.
        version_frontier (int): The limit between updating automatically and notifying the user.

    Returns:
        str: The latest version to which an automatic update can be performed.
    """    
    correctly_formatted_versions = filter_pep404_versions(img_versions)['correct_format']
    updatable_pep440_versions = [Version(v) for v in correctly_formatted_versions if Version(v) > Version(curr_version) and perform_automatic_update(curr_version, v, version_frontier)]
    return str(max(updatable_pep440_versions)) if updatable_pep440_versions else ''


def filter_pep404_versions(versions:list) -> dict:
    """ Distinguish between version numbers that have the correct format, and those who don't.
    All images versions should follow the PEP 440 standard - https://peps.python.org/pep-0440/

    Args:
        versions (list): All available versions to filter.

    Returns:
        dict: Filtered versions, divided by correct and incorrect format lists.
            The dict has the form {'correct_format':[...], 'incorrect_format':[...]}
    """    
    pep404_filtering = {'correct_format':[], 'incorrect_format':[]}
    for v in versions:
        if is_pep440(v):
            pep404_filtering['correct_format'].append(v)
        else:
            pep404_filtering['incorrect_format'].append(v)
    
    return pep404_filtering


def is_pep440(v:str) -> bool:
    """ Check if the given version number follows the PEP 440 standard.
    Version is used instead of version.parse() because it has been observed that the parse method also allows versions that don't follow the PEP 440 standard.

    Args:
        v (str): Version number to check.

    Raises:
        TypeError: If the version number is not a string.

    Returns:
        bool: True if the version number follows the PEP 440 standard, False otherwise.
    """    
    if not isinstance(v, str): raise TypeError('The parameter v must be a string.')
    try:
        Version(v)
        return True
    except InvalidVersion:
        return False


def get_newest_docker_updatable_version(updatable_versions:dict, version_frontier:int, latest_version_number:str) -> str:
    """ Return the last version the user can update to, according to the version frontier specified, for Docker images.

    Args:
        updatable_versions (dict): All available versions to filter.
        version_frontier (int): The limit between updating automatically and notifying the user.
        latest_version_number (str): The latest version available.

    Returns:
        str: The latest version to which an automatic update can be performed.
    """    
    latest_updatable_versions = [v for v in updatable_versions if perform_automatic_update(str(v), latest_version_number, version_frontier)]
    return 'latest' if latest_updatable_versions == ['latest'] else updatable_versions[max(latest_updatable_versions)]
