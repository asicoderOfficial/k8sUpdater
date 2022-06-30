

def perform_automatic_update(curr_version_number:str, latest_version_number:str, version_frontier:int) -> bool:
    """ Based on the user's specified latest_version_number, perform an update automatically, or not.
    The algorithm to check for updates is the following:
    1. Split the version numbers by dots, obtaining a list of the numbers in the original order.
    2. Base case: the version frontier is <= 0 or > len(curr_version_number_levels) -> Indicates update always.
    3. Get the shortest list (version number with less dots).
    4. Traverse from 0 to version_frontier-2, to check the latest surpasses current in the region the levels the user wants to avoid for automatic updates.
    If it outdated -> DO NOT UPDATE.
    5. Traverse from version_frontier-1 to the end of the shortest list. If it is outdated -> UPDATE.
    6. If no outdated version has been found while traversing, and the shortest version number turns out to be the current,
    it means that there are new smaller updates -> UPDATE.
    7. Else, DO NOT UPDATE, only notify, as the update may be bigger than expected

    Args:
        curr_version_number (str): Version number of the current image.
        latest_version_number (str): Version number of the latest image.
        version_frontier (int): The number that divides the update automatically/notify areas.
            A user may not want to automatically make big updates, as it may break production code with deprecations for instance.
            However, doing minor controlled updates without much supervision is recommended, as it improves security.
            Therefore, this variable defines a barrier. For example:
            -version_frontier = 2, curr_version_frontier=3.5.2.1, latest_version_number=4.6.2.2 -> 3.5|.2.1 & 4.6|.2.2 respectively.

    Returns:
        bool: Update automatically or not, True or False respectively.
    """    
    latest_version_levels = latest_version_number.split('.')
    curr_version_levels = curr_version_number.split('.')
    shortest_version_number = min(len(latest_version_levels), len(curr_version_levels))
    if version_frontier <= 0 or version_frontier > shortest_version_number:
        return True
    elif curr_version_number == latest_version_number:
        return False
    #Check if before the frontier, the versions are the same.
    for i in range(version_frontier):
        if latest_version_levels[i] > curr_version_levels[i]:
            return False
    #Check if after the frontier, the current version is outdated.
    for i in range(version_frontier, shortest_version_number):
        if latest_version_levels[i] > curr_version_levels[i]:
            return True
    if shortest_version_number == len(curr_version_levels):
        #Before and after the frontier the version is the same, and the shortest version number is the current:
        #there are newer versions with a higher level of granularity.
        return True
    return False
