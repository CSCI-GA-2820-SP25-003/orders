"""
Item class

Item class is a model for the item table in the database.

"""

import logging
from .persistent_base import db, PersistentBase, DataValidationError

logger = logging.getLogger("flask.app")


# Item table
class Item(db.Model, PersistentBase):
    """
    Class that represents an Item
    """

    # table fields
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey("order.id", ondelete="CASCADE"), nullable=True
    )
    name = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    # description = db.Column(db.String(256), nullable=True)

    def __repr__(self):
        return f"<Item {self.name} id=[{self.id}] price={self.price}>"

    # to dict

    # Add description back will cause data base error: Description is not a column of Item
    def serialize(self) -> dict:
        """Serializes an Item into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "order_id": self.order_id,
        }

    # to object
    def deserialize(self, data: dict) -> None:
        """Deserializes a Item from a dictionary"""
        try:
            self.name = data["name"]
            self.price = float(data["price"])
            self.quantity = int(data["quantity"])

            self.order_id = data.get("order_id")
        except KeyError as error:
            raise DataValidationError(
                "Invalid Item: missing " + error.args[0]
            ) from error
        except (TypeError, ValueError) as error:
            raise DataValidationError(
                "Invalid Item: incorrect data type " + str(error)
            ) from error
        return self
