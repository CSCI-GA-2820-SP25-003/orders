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
Test cases for Pet Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Item, Order, DataValidationError, db
from .factories import OrderFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  YourResourceModel   M O D E L   T E S T   C A S E S
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
