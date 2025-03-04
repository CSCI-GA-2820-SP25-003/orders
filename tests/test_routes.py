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
from service.models import db, Item, Order
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

    ################### H E L P E R     C O D E #########################
    def _create_orders(self, num):
        """Helper function to create orders in bulk"""
        orders = []

        for _ in range(num):
            order = OrderFactory()
            response = self.client.post("/orders", json=order.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "ERROR: Could not create order",
            )

            new_order = response.get_json()
            order.id = new_order["id"]
            orders.append(order)

        return orders

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    ################ TEST CASE FOR DELETING ORDERS ########################
    def test_delete_order(self):
        """Delete an order based on its order id"""
        order = self._create_orders(1)[0]
        resp = self.client.delete(f"/orders/{order.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # check if data is empty
        self.assertEqual(len(resp.data), 0)

        # check if the database returns 404
        resp = self.client.get(
            f"orders/{order.id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    ################ TEST CASE FOR DELETING ITEM ########################
    def test_delete_item(self):
        """Delete items from the order based on the order id"""
        order = self._create_orders(1)[0]

        # create order and assert
        response = self.client.post(
            "/orders", json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # create item and assert
        item = ItemFactory()

        response = self.client.post(
            f"orders/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Delete the item and assert
        response = self.client.delete(f"/orders/{order.id}/items/{item.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Assert if order no longer contain the item
        response = self.client.get(
            f"/orders/{order.id}/items/{item.id}", content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
