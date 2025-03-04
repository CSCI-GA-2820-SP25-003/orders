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
Test cases for Item Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Item, Order, DataValidationError, db
from .factories import OrderFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestItemModel(TestCase):
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
    #  T E S T   C A S E S  F O R   I T E M S
    ######################################################################

    def test_create_item(self):
        """Create an Order with an Item and add it to database"""
        # Get the list of all orders, should be []
        orders = Order.all()
        self.assertEqual(orders, [])

        # Create a dummy order and item corresponding to the order
        order = OrderFactory()
        item = ItemFactory(order=order)
        order.items.append(item)
        # make the order persist in the db
        order.create()

        # Check if order is in the db
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        # find order by id and assert
        new_order = Order.find(order.id)
        self.assertEqual(new_order.items[0].name, item.name)

        # create new item corresponding to same order
        item2 = ItemFactory(order=order)
        order.items.append(item2)
        order.update()

        # check if length of the list is 2
        new_order = Order.find(order.id)
        self.assertEqual(len(new_order.items), 2)
        self.assertEqual(new_order.items[1].name, item2.name)

    def test_serialization(self):
        """Item should be correctly serialized"""
        item = ItemFactory()
        json = item.serialize()

        self.assertEqual(json["id"], item.id)
        self.assertEqual(json["order_id"], item.order_id)
        self.assertEqual(json["name"], item.name)
        self.assertEqual(json["quantity"], item.quantity)
        self.assertEqual(json["price"], item.price)

    def test_deserialize(self):
        """Item should be correctly deserialized"""

        # dummy item
        item = ItemFactory()
        item.create()
        # create an item object containing the same values
        new_item = Item()
        new_item.deserialize(item.serialize())
        self.assertEqual(new_item.name, item.name)
        self.assertEqual(new_item.quantity, item.quantity)
        self.assertEqual(new_item.price, item.price)

    def test_item_repr(self):
        """Item should return a string representation"""
        item = ItemFactory()
        # check if item id and name is in the string representation
        self.assertIn(str(item.id), repr(item))
        self.assertIn(item.name, repr(item))

    def test_update_item_non_existant(self):
        """It should not update an item that is non existant"""
        item = ItemFactory()
        # set id to a value that will not exist in the db
        item.id = 0
        self.assertRaises(DataValidationError, item.update)

    def test_delete_non_existant(self):
        """It should not delete an item that is non existant"""
        item = ItemFactory()
        # set id to a value that will not exist in the db
        item.id = 0
        self.assertRaises(DataValidationError, item.delete)

    def test_deserialize_valid_data(self):
        """Test deserialization with valid data"""

        valid_data = {"name": "Laptop", "price": 1200.99, "quantity": 2, "order_id": 1}

        item = Item().deserialize(valid_data)
        self.assertEqual(item.name, "Laptop")
        self.assertEqual(item.price, 1200.99)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.order_id, 1)

    def test_deserialize_missing_field(self):
        """Test deserialization with missing required field"""

        missing_field_data = {"price": 1200.99, "quantity": 2}

        item = Item()
        with self.assertRaises(DataValidationError) as context:
            item.deserialize(missing_field_data)
        self.assertIn("Invalid Item: missing name", str(context.exception))

    def test_deserialize_invalid_type(self):
        """Test deserialization with incorrect data types"""

        invalid_type_data = {
            "name": "Laptop",
            "price": "free",  # Invalid type, should be float
            "quantity": "many",  # Invalid type, should be int
        }

        item = Item()
        with self.assertRaises(DataValidationError) as context:
            item.deserialize(invalid_type_data)
        self.assertIn("Invalid Item: incorrect data type", str(context.exception))
