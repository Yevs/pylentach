from configparser import ConfigParser
import os

class SimpleConfig(ConfigParser):
    """
    Simple class to make work with ConfigParser more convenient
    """

    DEFAULT_NAME = 'config.ini'
    DEFAULT_CONTENT = ''

    def __init__(self, *args, path=DEFAULT_NAME, content=DEFAULT_CONTENT, **kwargs):
        super().__init__()
        self.path = path
        self.content = content

    def exists(self):
        """
        Checks if config file exists.

        :return: Boolean value to check file existance
        """
        return os.path.isfile(self.path)

    def create(self):
        """
        Creates default config file

        :return: returns nothing
        """
        with open(self.path, 'w') as file:
            file.write(self.content)

    def save(self):
        """
        Saves config file.

        :return: returns nothing
        """
        with open(self.path, 'w') as config_file:
            self.write(config_file)

    def load(self):
        """
        Loads config file.

        :return: returns True if config file was loaded successfully
        """
        res = self.read(self.path)
        if not res:
            return False
        return True