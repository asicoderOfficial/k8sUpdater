from src.utilities.dates_times import docker_str_to_datetime
from src.docker_imgs.docker_versions_utilities import perform_automatic_update

import unittest
from datetime import datetime


class UtilitiesTests(unittest.TestCase):
    """ Class for testing the utilities developed in the src/utilities/ directory.
    """    

    def test_docker_str_to_datetime(self) -> None:
        """ Tests the conversion of a string containing a date in the format given by DockerHub to a datetime object.
        """        
        dt = '2022-06-15T13:14:25.654498Z'
        self.assertEqual(docker_str_to_datetime(dt), datetime(2022, 6, 15, 13, 14, 25))
        dt = '2022-06-15T13:14:25'
        self.assertEqual(docker_str_to_datetime(dt), datetime(2022, 6, 15, 13, 14, 25))


    def test_docker_perform_automatic_update(self) -> None:
        """ Tests the image automatic update checking.
        """        
        latest_version_number = '3.2.1'
        curr_version_number = '3.2.0'
        version_frontier = -1
        self.assertEqual(perform_automatic_update(curr_version_number, latest_version_number, version_frontier), True)

        ####Version numbers with same length####
        #Base case
        version_frontier = 5
        self.assertEqual(perform_automatic_update(curr_version_number, latest_version_number, version_frontier), True)
        #Latest is bigger before frontier, smaller after it
        version_frontier = 2
        latest_version_number = '4.2.1'
        curr_version_number = '3.2.2'
        self.assertEqual(perform_automatic_update(curr_version_number, latest_version_number, version_frontier), False)
        #Latest is bigger before frontier, and bigger after it as well
        latest_version_number = '4.2.5'
        self.assertEqual(perform_automatic_update(curr_version_number, latest_version_number, version_frontier), False)
        #Latest is equal before frontier, bigger after it.
        latest_version_number = '3.2.5'
        self.assertEqual(perform_automatic_update(curr_version_number, latest_version_number, version_frontier), True)
        #Both versions are equal.
        curr_version_number = '3.2.5'
        self.assertEqual(perform_automatic_update(curr_version_number, latest_version_number, version_frontier), False)

        ####Latest version number is shorter####
        latest_version_number = '3.2.1'
        curr_version_number = '3.1.2.1'
        #Base case
        version_frontier = 5
        self.assertEqual(perform_automatic_update(curr_version_number, latest_version_number, version_frontier), True)
        #Latest is bigger before frontier, smaller after it
        version_frontier = 2
        self.assertEqual(perform_automatic_update(curr_version_number, latest_version_number, version_frontier), False)
        #Latest is bigger before frontier, and bigger after it as well
        latest_version_number = '3.2.5'
        self.assertEqual(perform_automatic_update(curr_version_number, latest_version_number, version_frontier), False)
        #Latest is equal before frontier, bigger after it.
        latest_version_number = '3.1.5'
        self.assertEqual(perform_automatic_update(curr_version_number, latest_version_number, version_frontier), True)

        ####Current version number is shorter####
        latest_version_number = '3.2.1.1'
        curr_version_number = '3.1.2'
        #Base case
        version_frontier = 5
        self.assertEqual(perform_automatic_update(curr_version_number, latest_version_number, version_frontier), True)
        #Latest is bigger before frontier, smaller after it
        version_frontier = 2
        self.assertEqual(perform_automatic_update(curr_version_number, latest_version_number, version_frontier), False)
        #Latest is bigger before frontier, and bigger after it as well
        latest_version_number = '3.2.5.1'
        self.assertEqual(perform_automatic_update(curr_version_number, latest_version_number, version_frontier), False)
        #Latest is equal before frontier, bigger after it.
        latest_version_number = '3.1.5.1'
        self.assertEqual(perform_automatic_update(curr_version_number, latest_version_number, version_frontier), True)
        #Current is a substring from left to right of latest
        curr_version_number = '3.1.5'
        self.assertEqual(perform_automatic_update(curr_version_number, latest_version_number, version_frontier), True)


if __name__ == '__main__':
    unittest.main()
