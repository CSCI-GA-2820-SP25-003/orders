import logging
from datetime import datetime, timezone
from .persistent_base import db, PersistentBase, DataValidationError
from .items import Item
from enum import Enum

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

    def __repr__(self):
        return (
            f"<Order id=[{self.id}] customer={self.customer_name} status={self.status}>"
        )

    def serialize(self) -> dict:
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
    def find_by_name(cls, customer_name):
        """Returns all Orders with the given customer name"""
        logger.info("Processing customer name query for %s ...", customer_name)
        return cls.query.filter(cls.customer_name == customer_name).all()
