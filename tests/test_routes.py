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

    # H E L P E R     C O D E #########################
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

    # TEST CASES FOR CREATING ORDERS ########################
    def test_create_order(self):
        """Create an Order"""
        order = OrderFactory()
        response = self.client.post(
            "/orders", json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json = response.get_json()
        self.assertEqual(json["customer_name"], order.customer_name)
        self.assertEqual(json["status"], order.status.name)

    def test_create_order_with_invalid_data(self):
        """Not Create an Order with invalid data"""
        invalid_order = {"customer_name": "", "status": "INVALID"}
        response = self.client.post(
            "/orders", json=invalid_order, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_missing_data(self):
        """Not Create an Order with missing customer_name"""
        missing_data_order = {"status": "INVALID"}
        response = self.client.post(
            "/orders", json=missing_data_order, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_extra_data(self):
        """Create an Order with extra data"""
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

    # TEST CASES FOR DELETING ORDERS ########################
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

    # TEST CASES FOR UPDATE ORDERS ########################

    def test_update_order(self):
        """Update an existing order"""
        # create an order to update
        order = self._create_orders(1)[0]

        # update the order
        data = order.serialize()
        data["customer_name"] = "Updated Customer"
        data["status"] = "SHIPPED"

        # send the update request, update the order
        resp = self.client.put(
            f"/orders/{order.id}", json=data, content_type="application/json"
        )

        # assert that the update was successful
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # check if the data was actually updated
        updated_order = resp.get_json()
        self.assertEqual(updated_order["customer_name"], "Updated Customer")
        self.assertEqual(updated_order["status"], "SHIPPED")

        # verify through a GET request to test whether the updated version is in db now
        resp = self.client.get(f"/orders/{order.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        get_order = resp.get_json()
        self.assertEqual(get_order["customer_name"], "Updated Customer")
        self.assertEqual(get_order["status"], "SHIPPED")

    def test_update_order_not_found(self):
        """Return 404 when updating a non-existing order"""
        # create an order object but don't persist it (just for the data)
        # we need to work on the factories.py to get fuzzy objects in test cases
        order = OrderFactory()

        # try to update an order that doesn't exist (use id 0 which shouldn't exist since the sql starts from 1)
        resp = self.client.put(
            "/orders/0", json=order.serialize(), content_type="application/json"
        )

        # assert that update attempt returned NOT FOUND
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_with_invalid_data(self):
        """Not update an order when the data is invalid"""
        # create an order to update
        order = self._create_orders(1)[0]

        # create update data with invalid status
        invalid_data = order.serialize()
        # this is not a valid OrderStatus
        invalid_data["status"] = "INVALID_STATUS"

        # send update request with invalid data
        resp = self.client.put(
            f"/orders/{order.id}", json=invalid_data, content_type="application/json"
        )

        # the API should return 400 Bad Request for invalid data
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # verify the order was not updated by getting it
        resp = self.client.get(f"/orders/{order.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # the original status should remain unchanged
        get_order = resp.get_json()
        self.assertNotEqual(get_order["status"], "INVALID_STATUS")

    def test_update_order_with_missing_data(self):
        """Not update an order when required data is missing"""
        # create an order to update
        order = self._create_orders(1)[0]

        # create update data with missing required field (customer_name)
        incomplete_data = {
            "status": "SHIPPED"
            # missing customer_name which is required
        }

        # send update request with missing data
        resp = self.client.put(
            f"/orders/{order.id}", json=incomplete_data, content_type="application/json"
        )

        # the API should return 400 Bad Request for missing data
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # verify the order was not updated by getting it
        resp = self.client.get(f"/orders/{order.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # the original customer_name should remain unchanged
        get_order = resp.get_json()
        self.assertEqual(get_order["customer_name"], order.customer_name)

    def test_update_order_with_extra_data(self):
        """Ignore extra data when updating an order"""
        # create an order to update
        order = self._create_orders(1)[0]

        # prepare update data with valid fields plus an extra field
        update_data = order.serialize()
        update_data["customer_name"] = "Updated Customer"
        update_data["status"] = "SHIPPED"
        update_data["extra_field"] = "This field doesn't exist in the model"

        # send update request with extra data
        resp = self.client.put(
            f"/orders/{order.id}", json=update_data, content_type="application/json"
        )

        # the update should succeed, ignoring the extra field
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # verify the response contains updated data but not the extra field
        updated_order = resp.get_json()
        self.assertEqual(updated_order["customer_name"], "Updated Customer")
        self.assertEqual(updated_order["status"], "SHIPPED")
        self.assertNotIn("extra_field", updated_order)

        # verify through a GET request
        resp = self.client.get(f"/orders/{order.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        get_order = resp.get_json()
        self.assertEqual(get_order["customer_name"], "Updated Customer")
        self.assertEqual(get_order["status"], "SHIPPED")
        self.assertNotIn("extra_field", get_order)

    # TEST CASES FOR CREATING ITEMS ########################

    def test_create_item(self):
        """Create an Item for an Order"""
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
        """Not create an Item with invalid data"""
        order = self._create_orders(1)[0]
        invalid_item = {"name": "", "price": -1, "stock": -1}
        response = self.client.post(
            f"/orders/{order.id}/items",
            json=invalid_item,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_item_with_missing_data(self):
        """Not create an Item with missing data"""
        order = self._create_orders(1)[0]
        missing_data_item = {"price": 10.0, "stock": 5}
        response = self.client.post(
            f"/orders/{order.id}/items",
            json=missing_data_item,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_item_with_extra_data(self):
        """Create an Item with extra data"""
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

    # TEST CASES FOR DELETING ITEM ########################
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

    # TEST CASES FOR READING AN ORDER ################
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
        # orders = self._create_orders(1)

        response = self.client.get(
            f"/orders/{'invalid id'}", content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # TEST CASES FOR READING ITEM IN AN ORDER ################
    def test_read_item_in_order(self):
        orders = self._create_orders(1)
        test_order = orders[0]
        item = ItemFactory()
        item.order_id = test_order.id

        response = self.client.post(
            f"/orders/{test_order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        item_id = response.get_json()["id"]

        response = self.client.get(f"/orders/{test_order.id}/items/{item_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def read_item_in_order_doesnt_exist(self):
        orders = self._create_orders(1)
        test_order = orders[0]
        item = ItemFactory()

        response = self.client.post(
            f"/orders/{test_order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(f"/orders/{test_order.id}/items/{item.id + 1}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # TEST CASES FOR UPDATE ITEMS ########################

    def test_update_item_existing_order_existing_item(self):
        """Update an item with existing order id and existing item id"""
        # create an order
        order = self._create_orders(1)[0]

        # create an item for the order
        item = ItemFactory()
        response = self.client.post(
            f"/orders/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        # created item should return 201
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # get the created item's id
        item_data = response.get_json()
        item_id = item_data["id"]

        # update the item data
        update_data = item_data.copy()
        update_data["name"] = "Updated Item Name"
        update_data["price"] = 99.99
        update_data["quantity"] = 10

        # dend update request to update the item
        response = self.client.put(
            f"/orders/{order.id}/items/{item_id}",
            json=update_data,
            content_type="application/json",
        )

        # assert the update was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify the response data contains updated values
        updated_item = response.get_json()
        self.assertEqual(updated_item["name"], "Updated Item Name")
        self.assertEqual(updated_item["price"], 99.99)
        self.assertEqual(updated_item["quantity"], 10)

        # verify through a GET request to check if the updated version is in db now
        response = self.client.get(f"/orders/{order.id}/items/{item_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        get_item = response.get_json()
        self.assertEqual(get_item["name"], "Updated Item Name")
        self.assertEqual(get_item["price"], 99.99)
        self.assertEqual(get_item["quantity"], 10)

    def test_update_item_nonexisting_order_existing_item(self):
        """Return 404 when updating an item with non-existing order id"""
        # create an order and item
        order = self._create_orders(1)[0]

        # create an item for the order
        item = ItemFactory()
        response = self.client.post(
            f"/orders/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # get the created item's id
        item_data = response.get_json()
        item_id = item_data["id"]

        # try to update the item with a non-existing order id
        # assuming 0 is not a valid order id since the sql starts from 1
        non_existing_order_id = 0

        response = self.client.put(
            f"/orders/{non_existing_order_id}/items/{item_id}",
            json=item_data,
            content_type="application/json",
        )

        # assert that the update attempt returns 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item_existing_order_nonexisting_item(self):
        """Return 404 when updating a non-existing item for an existing order"""
        # create an order
        order = self._create_orders(1)[0]

        # create fake item data
        item = ItemFactory()

        # try to update a non-existing item
        # assuming 0 is not a valid item id since the sql starts from 1
        non_existing_item_id = 0

        response = self.client.put(
            f"/orders/{order.id}/items/{non_existing_item_id}",
            json=item.serialize(),
            content_type="application/json",
        )

        # assert that the update attempt returns 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item_nonexisting_order_nonexisting_item(self):
        """Return 404 when updating with both non-existing order and item ids"""
        # create fake item data
        item = ItemFactory()

        # try to update with non-existing order and item ids
        # assuming 0 is not a valid order id since the sql starts from 1
        non_existing_order_id = 0
        non_existing_item_id = 0

        response = self.client.put(
            f"/orders/{non_existing_order_id}/items/{non_existing_item_id}",
            json=item.serialize(),
            content_type="application/json",
        )

        # assert that the update attempt returns 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item_wrong_order_item_combination(self):
        """Return 404 when item exists but not in this order (not correct order-item combination)"""
        # Create two orders
        orders = self._create_orders(2)
        order1 = orders[0]
        order2 = orders[1]

        # create an item for order1
        item_1 = ItemFactory()
        response = self.client.post(
            f"/orders/{order1.id}/items",
            json=item_1.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # get the created item's id
        item_1_data = response.get_json()
        item_1_id = item_1_data["id"]

        # create an item for order2
        item_2 = ItemFactory()
        response = self.client.post(
            f"/orders/{order2.id}/items",
            json=item_2.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # try to update the item through order2
        response = self.client.put(
            f"/orders/{order2.id}/items/{item_1_id}",
            json=item_1_data,
            content_type="application/json",
        )

        # assert that the update attempt returns 404 since the item
        # exists but doesn't belong to order2
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item_with_invalid_input(self):
        """Not update an item when the data is invalid"""
        # create an order
        order = self._create_orders(1)[0]

        # create an item for the order
        item = ItemFactory()
        response = self.client.post(
            f"/orders/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # get the created item's id
        item_data = response.get_json()
        item_id = item_data["id"]

        # update with invalid price (string instead of number)
        item_data["price"] = "not-a-price"

        # send update request with invalid data
        response = self.client.put(
            f"/orders/{order.id}/items/{item_id}",
            json=item_data,
            content_type="application/json",
        )

        # the API should return 400 Bad Request for invalid data
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # verify the item was not updated
        response = self.client.get(f"/orders/{order.id}/items/{item_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        get_item = response.get_json()
        self.assertNotEqual(get_item["price"], "not-a-price")
        self.assertEqual(get_item["price"], item.price)

    def test_update_item_with_missing_input(self):
        """Not update an item when required data is missing"""
        # create an order
        order = self._create_orders(1)[0]

        # create an item for the order
        item = ItemFactory()
        response = self.client.post(
            f"/orders/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # get the created item's id
        item_data = response.get_json()
        item_id = item_data["id"]

        # create incomplete data (missing name field)
        incomplete_data = {
            "price": 99.99,
            "quantity": 5,
            # missing name which is required
        }

        # send update request with missing data
        response = self.client.put(
            f"/orders/{order.id}/items/{item_id}",
            json=incomplete_data,
            content_type="application/json",
        )

        # the API should return 400 Bad Request for missing data
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # verify the item was not updated
        response = self.client.get(f"/orders/{order.id}/items/{item_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        get_item = response.get_json()
        # name should remain unchanged
        self.assertEqual(get_item["name"], item.name)

    def test_update_item_with_extra_input(self):
        """Ignore extra data when updating an item"""
        # create an order
        order = self._create_orders(1)[0]

        # create an item for the order
        item = ItemFactory()
        response = self.client.post(
            f"/orders/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # get the created item's id
        item_data = response.get_json()
        item_id = item_data["id"]

        # prepare update data with valid fields plus an extra field
        update_data = item_data.copy()
        update_data["name"] = "Updated Item Name"
        update_data["extra_field"] = "This field doesn't exist in the model"

        # send update request with extra data
        response = self.client.put(
            f"/orders/{order.id}/items/{item_id}",
            json=update_data,
            content_type="application/json",
        )

        # the update should succeed, ignoring the extra field
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify the response contains updated data but not the extra field
        updated_item = response.get_json()
        self.assertEqual(updated_item["name"], "Updated Item Name")
        self.assertNotIn("extra_field", updated_item)

        # verify through a GET request
        response = self.client.get(f"/orders/{order.id}/items/{item_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        get_item = response.get_json()
        self.assertEqual(get_item["name"], "Updated Item Name")
        self.assertNotIn("extra_field", get_item)

    # TEST CASES FOR LIST ORDERS ########################
    def test_list_orders(self):
        """Test listing all orders"""
        # Create a set of orders for testing
        orders = []
        for i in range(5):
            order = self._create_orders(1)[0]
            orders.append(order)

        # Send a request to the list endpoint
        resp = self.client.get("/orders")

        # Check response
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()

        # Check structure of the response
        self.assertIn("orders", data)
        self.assertIn("metadata", data)

        # Check that we got all the orders we created
        self.assertEqual(len(data["orders"]), 5)
        self.assertEqual(data["metadata"]["total_items"], 5)

    def test_list_orders_by_status(self):
        """Test listing orders filtered by status"""
        # from service.models import OrderStatus

        # Create several orders (the _create_orders method should create them with default statuses)
        orders = []
        for _ in range(5):
            order = self._create_orders(1)[0]
            orders.append(order)

        # Get the status of one of the orders to use for filtering
        test_order = orders[0]
        status_to_filter = test_order.status
        status_value = (
            status_to_filter.value
            if hasattr(status_to_filter, "value")
            else str(status_to_filter)
        )

        print(f"Filtering by status: {status_to_filter} (value: {status_value})")

        # Count how many orders have this status
        matching_orders = [o for o in orders if o.status == status_to_filter]
        expected_count = len(matching_orders)
        print(
            f"Expected to find {expected_count} orders with status {status_to_filter}"
        )

        # Send request to filter by this status
        resp = self.client.get(f"/orders?status={status_value}")

        # Check response
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        print(f"Response data: {data}")

        # Ensure we found the expected number of orders
        self.assertEqual(len(data["orders"]), expected_count)

        # Verify all returned orders have the right status
        for order_data in data["orders"]:
            self.assertEqual(order_data["status"], status_value)

    def test_list_orders_with_pagination(self):
        """Test listing orders with pagination"""
        # Create 15 orders to test pagination
        orders = []
        for i in range(15):
            order = self._create_orders(1)[0]
            orders.append(order)

        # Get first page (default is 10 per page)
        resp = self.client.get("/orders")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data["orders"]), 10)
        self.assertEqual(data["metadata"]["page"], 1)
        self.assertEqual(data["metadata"]["total_items"], 15)

        # Get second page (remaining 5 orders)
        resp = self.client.get("/orders?page=2")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data["orders"]), 5)
        self.assertEqual(data["metadata"]["page"], 2)

        # Test custom page size
        resp = self.client.get("/orders?page=1&page_size=5")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data["orders"]), 5)
        self.assertEqual(data["metadata"]["page_size"], 5)
        self.assertEqual(data["metadata"]["total_pages"], 3)

    # TEST CASES FOR LIST ITEMS IN AN ORDER ############
    def test_list_items(self):
        """It should List all Items in an Order"""
        # Create an order first
        order = self._create_orders(1)[0]
        self.assertIsNotNone(order)

        # Create a few items for this order
        items = []
        for _ in range(3):
            item = ItemFactory()
            response = self.client.post(
                f"/orders/{order.id}/items",
                json=item.serialize(),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            items.append(response.get_json())

        # Send a request to list items
        response = self.client.get(f"/orders/{order.id}/items")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the response
        data = response.get_json()
        self.assertEqual(len(data), 3)

        # Verify the items match what we created
        item_ids = [item["id"] for item in data]
        for item in items:
            self.assertIn(item["id"], item_ids)
