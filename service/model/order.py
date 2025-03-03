import logging
from datetime import datetime
from .models import db, PersistentBase, DataValidationError
from .items import Item

logger = logging.getLogger("flask.app")


class Order(db.Model, PersistentBase):
    """
    Class that represents an Order
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(64), nullable=False)
    # like pending, shipped, completed
    status = db.Column(db.String(32), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    items = db.relationship("Item", backref="order", passive_deletes=True)

    def __repr__(self):
        return (
            f"<Order id=[{self.id}] customer={self.customer_name} status={self.status}>"
        )

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "items": [item.serialize() for item in self.items],
        }

    def deserialize(self, data: dict) -> None:
        try:
            self.customer_name = data["customer_name"]
            self.status = data.get("status", "pending")
            self.created_at = (
                datetime.fromisoformat(data["created_at"])
                if "created_at" in data
                else datetime.utcnow()
            )

            item_list = data.get("items", [])
            self.items = []
            for json_item in item_list:
                item = Item()
                item.deserialize(json_item)
                self.items.append(item)
        except KeyError as error:
            raise DataValidationError(
                "Invalid Order: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Order: incorrect data type " + str(error)
            ) from error
        return self

    @classmethod
    def find_by_name(cls, customer_name):
        """Returns all Orders with the given customer name"""
        logger.info("Processing customer name query for %s ...", customer_name)
        return cls.query.filter(cls.customer_name == customer_name)
