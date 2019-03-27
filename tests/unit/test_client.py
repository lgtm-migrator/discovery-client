"""Test Consul standard client module."""
import logging
import os
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

import consul

from discovery import client

import requests


class TestClient(unittest.TestCase):
    """Unit tests to Consul standard client."""

    def setUp(self):
        """Mock of responses generated by python-consul.

        and expected results generated by discovery-client.
        """
        self.consul_health_response = (
            0, [{'Node': {
                'ID': '123456'}}])
        self.consul_raw_response = (
            0, [{'Node': 'localhost',
                 'Address': '127.0.0.1',
                 'ServiceID': '#123',
                 'ServiceName': 'consul',
                 'ServicePort': 8300}])
        self.myapp_raw_response = (
            0, [{'Node': 'localhost',
                 'ID': '987654',
                 'Address': '127.0.0.1',
                 'ServiceID': '#987',
                 'ServiceName': 'myapp',
                 'ServicePort': 5000}])
        self.fmt_response = [
            {
                'node': 'localhost',
                'address': '127.0.0.1',
                'service_id': '#123',
                'service_name': 'consul',
                'service_port': 8300
            },
            {
                'node': 'localhost',
                'address': '127.0.0.1',
                'service_id': '#987',
                'service_name': 'myapp',
                'service_port': 5000
            }]

    def test_changing_default_timeout(self):
        """Test change the time used to check periodically health status of the Consul connection."""
        os.environ['DEFAULT_TIMEOUT'] = '5'
        dc = client.Consul('localhost', 8500)

        self.assertEqual(dc.DEFAULT_TIMEOUT, 5)
        self.assertNotEqual(dc.DEFAULT_TIMEOUT, 30)

    @patch('discovery.client.consul.Consul')
    def test_find_services(self, MockConsul):
        """Test for localization of a set of services present in the consul's catalog.

        Return a list of instances present in the consul's catalog.
        """
        consul_client = MockConsul(consul.Consul)
        consul_client.catalog.service = MagicMock(
            return_value=self.consul_raw_response
        )

        dc = client.Consul('localhost', 8500)
        consul_service = dc.find_services('consul')

        self.assertIsInstance(consul_service, list)
        self.assertIn(self.fmt_response[0], consul_service)

    @patch('discovery.client.consul.Consul')
    def test_find_services_not_on_catalog(self, MockConsul):
        """Test for localization of a set of services not present in the consul's catalog.

        Return a empty list.
        """
        consul_client = MockConsul(consul.Consul)
        consul_client.catalog.service = MagicMock(return_value=(0, []))

        dc = client.Consul('localhost', 8500)
        response = dc.find_services('myapp')

        self.assertEqual(response, [])

    @patch('discovery.client.consul.Consul')
    def test_find_service_not_found(self, MockConsul):
        """Test for localization of a service not present in the consul's catalog.

        Raise IndexError execption.
        """
        consul_client = MockConsul(consul.Consul)
        consul_client.catalog.service = MagicMock(return_value=(0, []))

        dc = client.Consul('localhost', 8500)

        with self.assertRaises(IndexError):
            dc.find_service('myapp')

    @patch('discovery.client.consul.Consul')
    def test_find_service_rr(self, MockConsul):
        """Test for localization of a service present in the consul's catalog.

        Return instances in round robin method, when there is more than
        one registered.
        """
        consul_client = MockConsul(consul.Consul)
        consul_client.catalog.service = MagicMock(
            return_value=self.consul_raw_response
        )

        dc = client.Consul('localhost', 8500)
        consul_service = dc.find_service('consul')

        self.assertIsInstance(consul_service, dict)
        self.assertEqual(consul_service, self.fmt_response[0])

    @patch('discovery.client.consul.Consul')
    def test_find_service_random(self, MockConsul):
        """Test for localization of a service present in the consul's catalog.

        Return random instances, when there is more than one registered.
        """
        consul_client = MockConsul(consul.Consul)
        consul_client.catalog.service = MagicMock(
            return_value=self.consul_raw_response
        )

        dc = client.Consul('localhost', 8500)
        consul_service = dc.find_service('consul', method='random')

        self.assertIsInstance(consul_service, dict)
        self.assertEqual(consul_service, self.fmt_response[0])

    @patch('discovery.client.consul.Consul')
    def test_register(self, MockConsul):
        """Test registration of a service in the  consul's catalog."""
        consul_client = MockConsul(consul.Consul)
        consul_client.agent.service.register = MagicMock()
        consul_client.catalog.service = MagicMock(
            return_value=self.myapp_raw_response
        )

        dc = client.Consul('localhost', 8500)
        dc.register('myapp', 5000)
        myapp_service = dc.find_service('myapp')

        self.assertIsInstance(myapp_service, dict)
        self.assertEqual(myapp_service, self.fmt_response[1])

    @patch('discovery.client.consul.Consul')
    def test_register_connection_error(self, MockConsul):
        """Failure test to register a service when there is no instance of consul available."""
        consul_client = MockConsul(consul.Consul)
        consul_client.agent.service.register = MagicMock(
            side_effect=requests.exceptions.ConnectionError
        )
        consul_client.health.service = MagicMock(
            side_effect=requests.exceptions.ConnectionError
        )

        dc = client.Consul('localhost', 8500)
        with self.assertLogs() as cm:
            logging.getLogger(dc.register('myapp', 5000))
        self.assertEqual(
            cm.output, ['ERROR:root:Failed to connect to discovery...']
        )

    @patch('discovery.client.consul.Consul')
    def test_deregister(self, MockConsul):
        """Test the deregistration of a service present in the consul's catalog."""
        consul_client = MockConsul(consul.Consul)
        consul_client.agent.service.register = MagicMock()
        consul_client.agent.service.deregister = MagicMock()
        consul_client.catalog.service = MagicMock(
            return_value=self.myapp_raw_response
        )

        dc = client.Consul('localhost', 8500)
        dc.register('myapp', 5000)
        myapp_service = dc.find_service('myapp')

        self.assertIsInstance(myapp_service, dict)
        self.assertEqual(myapp_service, self.fmt_response[1])

        dc.deregister()

        consul_client.catalog.service = MagicMock(return_value=(0, []))

        with self.assertRaises(IndexError):
            myapp_service = dc.find_service('myapp')


if __name__ == '__main__':
    unittest.main()