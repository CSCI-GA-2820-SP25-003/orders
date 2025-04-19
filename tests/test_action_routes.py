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
TestYourResourceModel API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Order
from tests.factories import OrderFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def test_cancel_order(self):
        """change status of order to CANCELLED"""
        item = ItemFactory()
        order = item.order
        order.status = "CREATED"
        order.create()

        response = self.client.put(f"api/orders/{order.id}/cancel")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cancel_bad_order(self):
        """cancel order that does not exist"""
        order = OrderFactory()
        order.status = "CREATED"
        order.create()

        response = self.client.put("api/orders/0/cancel")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_status(self):
        """update the status of an order"""
        order = OrderFactory()
        order.status = "PENDING"
        order.create()

        # create item and assert
        item = ItemFactory()

        response = self.client.post(
            f"api/orders/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.put(f"api/orders/{order.id}/update")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.status.value, "CREATED")

    def test_update_bad_order(self):
        """Try to update order that does not exist"""
        order = OrderFactory()
        order.status = "CREATED"
        order.create()

        # create item and assert
        item = ItemFactory()

        response = self.client.post(
            f"api/orders/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.put("api/orders/0/update")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_empty_order(self):
        """Update order with empty item list"""
        order = OrderFactory()
        order.status = "CREATED"
        order.create()

        response = self.client.put(f"api/orders/{order.id}/update")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_completed_order(self):
        """Try to update order that is completed"""
        order = OrderFactory()
        order.status = "COMPLETED"
        order.create()

        # create item and assert
        item = ItemFactory()

        response = self.client.post(
            f"api/orders/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.put(f"api/orders/{order.id}/update")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_cancelled_order(self):
        """Try to update order that is cancelled"""
        order = OrderFactory()
        order.status = "CANCELLED"
        order.create()

        # create item and assert
        item = ItemFactory()

        response = self.client.post(
            f"api/orders/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.put(f"api/orders/{order.id}/update")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
