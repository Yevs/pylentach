from configparser import ConfigParser
from pylentach.SimpleConfig import SimpleConfig
import unittest
import os

class SimpleConfigTest(unittest.TestCase):

    def setUp(self):
        self.config = SimpleConfig()

    def deleteIfExists(self):
        if os.path.isfile(self.config.path):
            os.remove(self.config.path)

    def test_init(self):   
        self.assertEqual(self.config.path, 'config.ini')

    def test_exists(self):
        self.assertEqual(os.path.isfile('config.ini'), self.config.exists())
        open('config.ini', 'w').close()
        self.assertEqual(self.config.exists(), True)

    def test_create(self):
        data = 'some test data'
        self.config = SimpleConfig(content=data)
        self.config.create()
        self.assertTrue(os.path.isfile('config.ini'))
        with open('config.ini', 'r') as file:
            read_data = ''
            for line in file:
                read_data += line
        self.assertEqual(read_data, data)
        self.config = SimpleConfig()

    def test_load(self):
        self.deleteIfExists()
        self.assertFalse(self.config.load())

    def test_save(self):
        self.config['DEFAULT']['abc'] = '3'
        self.config.save()
        expecteds = ['[DEFAULT]', 'abc = 3']
        with open('config.ini', 'r') as file:
            for line, expected in zip(file, expecteds):
                self.assertEqual(line.strip(), expected.strip())
        self.config = SimpleConfig()

    def tearDown(self):
        self.deleteIfExists()