# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
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

"""
Test Factory to make fake objects for testing
"""
from datetime import date
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate, FuzzyInteger
from service.models import Item, Order, OrderStatus


class OrderFactory(factory.Factory):
    """Creates fake Orders"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Order

    id = factory.Sequence(lambda n: n)
    customer_name = factory.Faker("name")
    status = FuzzyChoice(list(OrderStatus))
    created_at = FuzzyDate(date(2008, 1, 1))
    updated_at = FuzzyDate(date(2008, 9, 8))

    # For items in the order
    @factory.post_generation
    def items(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.items = extracted


class ItemFactory(factory.Factory):
    """Creates fake Item"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Item

    id = factory.Sequence(lambda n: n)
    order_id = None
    name = FuzzyChoice(
        choices=[
            "Electronics",
            "Clothing",
            "Books",
            "Toys",
            "Furniture",
        ]
    )
    quantity = FuzzyInteger(1, 5)
    price = FuzzyInteger(10, 50)
    order = factory.SubFactory(OrderFactory)
