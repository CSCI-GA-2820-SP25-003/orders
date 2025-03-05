######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Error Handlers for Flask
"""

import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import DataValidationError


class ErrorHandlerTester(TestCase):
    """ "Tests for error handler"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()

    # TEST CASES #######

    def test_data_validation_error(self):
        """Test handling of DataValidationError"""
        with app.test_request_context():
            response, status_code = app.handle_user_exception(
                DataValidationError("Invalid data provided")
            )

        self.assertEqual(status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid data provided", response.get_json()["message"])

    def test_405_not_allowed(self):
        """Test for 405 method not allowed"""
        response = self.client.put("/orders")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_415_unsupported_type(self):
        """Test for 415 unsupported type"""

        # make a post request using plaintext as the type
        response = self.client.post(
            "/orders", data="dummy entry", content_type="text/plain"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        response = self.client.post("/orders", data="dummy entry")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_500_server_error(self):
        """Test for 500 server error"""

        # trigger the 500 error and assert
        response = self.client.get("/500_error")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
