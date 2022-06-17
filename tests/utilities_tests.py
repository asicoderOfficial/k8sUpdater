from src.utilities.dates_times import docker_str_to_datetime

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


if __name__ == '__main__':
    unittest.main()
