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

    def test_health(self):
        """It should call the health endpoint"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    ################ TEST CASES FOR CREATING ORDERS ########################
    def test_create_order(self):
        """It should Create an Order"""
        order = OrderFactory()
        response = self.client.post(
            "/orders", json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json = response.get_json()
        self.assertEqual(json["customer_name"], order.customer_name)
        self.assertEqual(json["status"], order.status.name)

    def test_create_order_with_invalid_data(self):
        """It should not Create an Order with invalid data"""
        invalid_order = {"customer_name": "", "status": "INVALID"}
        response = self.client.post(
            "/orders", json=invalid_order, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_missing_data(self):
        """It should not Create an Order with missing customer_name"""
        missing_data_order = {"status": "INVALID"}
        response = self.client.post(
            "/orders", json=missing_data_order, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_extra_data(self):
        """It should Create an Order with extra data"""
        order = OrderFactory()
        extra_data_order = order.serialize()
        extra_data_order["extra_field"] = "extra_value"
        response = self.client.post(
            "/orders", json=extra_data_order, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json = response.get_json()
        self.assertNotIn("extra_field", json)
        self.assertEqual(json["customer_name"], order.customer_name)
        self.assertEqual(json["status"], order.status.name)

    ################ TEST CASES FOR CREATING ITEMS ########################
    def test_create_item(self):
        """It should Create an Item for an Order"""
        order = self._create_orders(1)[0]
        item = ItemFactory()
        response = self.client.post(
            f"/orders/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json = response.get_json()
        self.assertEqual(json["name"], item.name)
        self.assertEqual(json["price"], item.price)
        self.assertEqual(json["quantity"], item.quantity)

    def test_create_item_with_invalid_data(self):
        """It should not Create an Item with invalid data"""
        order = self._create_orders(1)[0]
        invalid_item = {"name": "", "price": -1, "stock": -1}
        response = self.client.post(
            f"/orders/{order.id}/items",
            json=invalid_item,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_item_with_missing_data(self):
        """It should not Create an Item with missing data"""
        order = self._create_orders(1)[0]
        missing_data_item = {"price": 10.0, "stock": 5}
        response = self.client.post(
            f"/orders/{order.id}/items",
            json=missing_data_item,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_item_with_extra_data(self):
        """It should Create an Item with extra data"""
        order = self._create_orders(1)[0]
        item = ItemFactory()
        extra_data_item = item.serialize()
        extra_data_item["extra_field"] = "extra_value"
        response = self.client.post(
            f"/orders/{order.id}/items",
            json=extra_data_item,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json = response.get_json()
        self.assertNotIn("extra_field", json)
        self.assertEqual(json["name"], item.name)
        self.assertEqual(json["price"], item.price)
        self.assertEqual(json["quantity"], item.quantity)

    ################ TEST CASES FOR DELETING ORDERS ########################
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

    def test_delete_order_no_order_id(self):
        """Delete an order with no order id"""
        # Create an order
        _ = self._create_orders(1)[0]

        # delete an order with no order id
        resp = self.client.delete("/orders/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    ################ TEST CASES FOR DELETING ITEM ########################
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

        json = response.get_json()
        item_id = json["id"]
        # Delete the item and assert
        response = self.client.delete(f"/orders/{order.id}/items/{item_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Assert if order no longer contain the item
        response = self.client.get(
            f"/orders/{order.id}/items/{item_id}", content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item_no_order(self):
        """Try to delete item with no order id"""
        item = ItemFactory()

        # Try and add item to a non existing order
        response = self.client.post(
            "/orders/0/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(f"/orders/0/items/{item.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item_no_id(self):
        """Try to delete an item from an order with no item id"""
        # create an order
        order = self._create_orders(1)[0]

        # try to delete an item from the order
        response = self.client.delete(f"/orders/{order.id}/items/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # TEST CASES FOR READING AN ORDER
    def test_read_order(self):
        orders = self._create_orders(1)
        test_order = orders[0]

        response = self.client.get(
            f"/orders/{test_order.id}", content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_order_doesnt_exist(self):
        orders = self._create_orders(1)
        test_order = orders[0]

        response = self.client.get(
            f"/orders/{test_order.id + 1}", content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_read_order_invalid_id(self):
        orders = self._create_orders(1)

        response = self.client.get(
            f"/orders/{'invalid id'}", content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
