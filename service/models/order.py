"""Order Model

This module contains the Order model.
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from .persistent_base import db, PersistentBase, DataValidationError
from .items import Item


logger = logging.getLogger("flask.app")


# Define the order status to be used
class OrderStatus(Enum):
    """Enum for valid order status"""

    PENDING = "PENDING"
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    SHIPPED = "SHIPPED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

    @staticmethod
    def list():
        """Lists different order statuses"""
        return list(map(lambda s: s.value, OrderStatus))


class Order(db.Model, PersistentBase):
    """
    Class that represents an Order
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(64), nullable=False)
    # like pending, shipped, completed
    status = db.Column(
        db.Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING
    )
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    items = db.relationship("Item", backref="order", passive_deletes=True)

    """return a string representation of the order"""

    def __repr__(self):
        return (
            f"<Order id=[{self.id}] customer={self.customer_name} status={self.status}>"
        )

    def serialize(self) -> dict:
        """Serialize an Order into a dictionary"""
        if not isinstance(self.status, OrderStatus):
            raise DataValidationError(
                f"Invalid status value '{self.status}' not in OrderStatus Enum"
            )

        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "items": [item.serialize() for item in self.items],
        }

    def deserialize(self, data: dict) -> None:
        """Deserialize an Order from a dictionary"""
        try:
            self.customer_name = data["customer_name"]

            # Ensure status is properly converted to ENUM
            status_str = data.get("status", "PENDING")  # Default to "PENDING"
            if (
                isinstance(status_str, str)
                and status_str.upper() in OrderStatus.__members__
            ):
                self.status = OrderStatus[status_str.upper()]  # Convert string to ENUM
            else:
                raise DataValidationError(
                    f"Invalid status: {status_str}. Allowed values: {OrderStatus.list()}"
                )

            self.created_at = (
                datetime.fromisoformat(data["created_at"])
                if "created_at" in data
                else datetime.now(timezone.utc)
            )
            item_list = data.get("items", [])
            for json_item in item_list:
                item = Item()
                item.deserialize(json_item)
                self.items.append(item)

        except KeyError as error:
            raise DataValidationError(
                f"Invalid Order: missing {error.args[0]}"
            ) from error
        except (TypeError, ValueError) as error:
            raise DataValidationError(f"Invalid Order: {str(error)}") from error

        return self

    @classmethod
    def find_by_filters(
        cls, customer_name=None, order_status=None, order_id=None, product_name=None
    ):
        """
        Returns all Orders matching the given filters.

        Args:
            customer_name (str, optional): Name of the customer whose orders you want.
            order_status (str, optional): Status of the orders to filter.
            order_id (str, optional): Order ID of the orders to filter.

        Returns:
            List of matching Order objects.
        """
        query = cls.query
        if customer_name:
            query = query.filter(cls.customer_name == customer_name)
        if order_status:
            order_status = order_status.upper()
            if order_status in OrderStatus.list():
                query = query.filter(cls.status == OrderStatus[order_status])
            else:
                query = query.filter(False)
        if order_id:
            query = query.filter(cls.id == order_id)
        if product_name:
            query = query.join(Item).filter(Item.name == product_name)
        return query.all()
