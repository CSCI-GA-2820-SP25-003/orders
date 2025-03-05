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
Test cases for Order Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Order, DataValidationError, db
from .factories import OrderFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestOrderModel(TestCase):
    """Test Cases for YourResourceModel Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S  F O R   O R D E R S
    ######################################################################

    def test_create_order(self):
        """It should create an Order"""
        faker = OrderFactory()

        order = Order(
            id=faker.id,
            customer_name=faker.customer_name,
            status=faker.status,
            created_at=faker.created_at.isoformat(),
            updated_at=faker.updated_at.isoformat(),
            items=faker.items,
        )

        # assert the order
        self.assertIsNotNone(order)
        self.assertEqual(order.id, faker.id)
        self.assertEqual(order.customer_name, faker.customer_name)
        self.assertEqual(order.status, faker.status)
        self.assertEqual(order.created_at, faker.created_at.strftime("%Y-%m-%d"))
        self.assertEqual(order.updated_at, faker.updated_at.strftime("%Y-%m-%d"))
        self.assertEqual(len(order.items), len(faker.items))

    def test_list_all_orders(self):
        """It should list all orders in the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        for order in OrderFactory.create_batch(3):
            order.create()
        # Assert that there are 3 orders in the database
        orders = Order.all()
        self.assertEqual(len(orders), 3)

    def test_find_by_name(self):
        """Should return the order by name"""
        order = OrderFactory()
        order.customer_name = "dev"
        order.create()

        named_order = Order.find_by_name("dev")
        self.assertGreater(len(named_order), 0)  # Ensure we got at least one result
        self.assertEqual(named_order[0].customer_name, "dev")

    def test_serialization(self):
        """Order should be correctly serialized"""
        # create a dummy order and item
        order = OrderFactory()
        item = ItemFactory()

        # add item to order
        order.items.append(item)
        serialized_order = order.serialize()
        # assert
        self.assertEqual(serialized_order["id"], order.id)
        self.assertEqual(serialized_order["customer_name"], order.customer_name)
        self.assertEqual(serialized_order["status"], order.status.value)
        self.assertEqual(serialized_order["created_at"], str(order.created_at))
        self.assertEqual(serialized_order["updated_at"], str(order.updated_at))
        self.assertEqual(len(serialized_order["items"]), 1)

        # assert for items in the order
        items_list = serialized_order["items"]
        self.assertEqual(items_list[0]["id"], item.id)
        self.assertEqual(items_list[0]["order_id"], item.order_id)
        self.assertEqual(items_list[0]["name"], item.name)
        self.assertEqual(items_list[0]["quantity"], item.quantity)
        self.assertEqual(items_list[0]["price"], item.price)

    def test_deserialization(self):
        """ "Order should be correctly deserialized"""

        # create dummy order and item
        order = OrderFactory()
        item = ItemFactory()
        order.items.append(item)

        serialized_order = order.serialize()
        # create an empty order and store values into it
        new_order = Order()
        new_order.deserialize(serialized_order)
        # assert
        self.assertEqual(new_order.customer_name, order.customer_name)
        self.assertEqual(new_order.status, order.status)

    def test_data_invalid_status(self):
        """Test serialization and deserialization with invalid status value"""
        order = OrderFactory()
        order_json = order.serialize()
        order_json["status"] = "INVALID_STATUS"  # Assign an invalid status

        self.assertRaises(DataValidationError, order.deserialize, order_json)

        order.status = "INVALID_STATUS"
        self.assertRaises(DataValidationError, order.serialize)

    def test_deserialize_with_errors(self):
        """Test for deserialization for various conditions"""
        # create dummy order with no data
        order = Order()

        """Key Error"""
        self.assertRaises(DataValidationError, order.deserialize, {})

        """Type Error"""
        self.assertRaises(DataValidationError, order.deserialize, [])

    def test_order_no_name(self):
        """Order should not be created with no name"""
        order = Order()
        self.assertRaises(DataValidationError, order.create)

    def test_update_order_no_id(self):
        """It should not update an order that doesnt exist"""
        order = OrderFactory()
        order.id = 0
        self.assertRaises(DataValidationError, order.update)

    def test_delete_order_no_id(self):
        """It should not delete an order that doesnt exist"""
        order = OrderFactory()
        order.id = 0
        self.assertRaises(DataValidationError, order.delete)
