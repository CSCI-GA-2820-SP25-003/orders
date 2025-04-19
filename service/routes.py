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
YourResourceModel Service

This service implements a REST API that allows you to Create, Read, Update
and Delete YourResourceModel
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from flask_restx import Api, Resource, fields
from service.models import Item, Order, OrderStatus
from service.common import status  # HTTP Status Codes


######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Order Demo REST API Service",
    description="This is a Order server.",
    default="orders",
    default_label="Order operations",
    doc="/apidocs",  # default also could use doc='/apidocs/'
    prefix="/api",
)


# Define the models so that the docs reflect what can be sent
item_model = api.model(
    "Item",
    {
        "id": fields.Integer(readonly=True, description="The unique ID of the item"),
        "order_id": fields.Integer(description="ID of the order this item belongs to"),
        "name": fields.String(required=True, description="Name of the product"),
        "price": fields.Float(required=True, description="Price of the product"),
        "quantity": fields.Integer(
            required=True, description="Quantity of the product"
        ),
    },
)


order_model = api.model(
    "Order",
    {
        "id": fields.Integer(readonly=True, description="The unique ID of the order"),
        "customer_name": fields.String(
            required=True, description="Name of the customer"
        ),
        "status": fields.String(
            required=True, description="Order status", enum=OrderStatus.list()
        ),
        "created_at": fields.DateTime(
            readonly=True, description="Order creation timestamp"
        ),
        "updated_at": fields.DateTime(
            readonly=True, description="Order last updated timestamp"
        ),
        "items": fields.List(
            fields.Nested(item_model), description="List of items in the order"
        ),
    },
)


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file("index.html")


######################################################################
#  R E S T   A P I   E N D P O I N T S  F O R  O R D E R S
######################################################################


######################################################################
#  LIST ORDERS BASED ON QUERY
######################################################################
@api.route("/orders", strict_slashes=False)
class OrderCollection(Resource):
    """Handles all interactions with collections of Orders"""

    # ------------------------------------------------------------------
    # LIST ALL ORDERS
    # ------------------------------------------------------------------
    @api.marshal_list_with(order_model)
    def get(self):
        """Get Orders"""
        customer_name = request.args.get("customer_name")
        order_id = request.args.get("order_id", type=int)
        product_name = request.args.get("product_name")
        status_val = request.args.get("status")
        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("page_size", 10, type=int)

        # Get all orders
        filtered_orders = Order.find_by_filters(
            customer_name=customer_name,
            order_status=status_val,
            order_id=order_id,
            product_name=product_name,
        )

        app.logger.info(
            f"After filtering: {len(filtered_orders)} orders match criteria"
        )

        # Apply pagination
        # total_items = len(filtered_orders)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paged_orders = filtered_orders[start_idx:end_idx]

        # Calculate total pages
        # total_pages = (
        #     (total_items + page_size - 1) // page_size if total_items > 0 else 0
        # )

        # Create response
        results = [order.serialize() for order in paged_orders]

        # response = {
        #     "orders": results,
        #     "metadata": {
        #         "page": page,
        #         "page_size": page_size,
        #         "total_items": total_items,
        #         "total_pages": total_pages,
        #     },
        # }

        app.logger.info(f"Returning {len(results)} orders")
        return results, status.HTTP_200_OK

    @api.expect(order_model)
    @api.marshal_with(order_model, code=201)
    def post(self):
        """Post orders"""
        app.logger.info("Request to create an Order")
        check_content_type("application/json")

        # create the order
        order = Order()
        order.deserialize(request.get_json())
        order.create()

        # create a message to return
        message = order.serialize()

        return message, status.HTTP_201_CREATED


######################################################################
#  RETRIEVE AN ORDER
######################################################################
@api.route("/orders/<int:order_id>", strict_slashes=False)
@api.param("order_id", "The Order identifier")
class OrderResource(Resource):
    """Order Operations"""

    @api.marshal_with(order_model)
    def get(self, order_id):
        """Get an Order by its ID"""
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )

        return order.serialize(), status.HTTP_200_OK

    @api.expect(order_model)
    @api.marshal_with(order_model)
    def put(self, order_id):
        """Update an Order"""
        app.logger.info(f"Request to update order id:{order_id}")
        order = Order.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND, f"Order {order_id} not found")
        order.deserialize(api.payload)
        order.id = order_id
        order.update()
        return order.serialize(), status.HTTP_200_OK

    def delete(self, order_id):
        """Delete order using the order id"""
        app.logger.info("Request to delete an order with id: %s", order_id)
        order = Order.find(order_id)
        if order:
            order.delete()
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  ACTION ROUTE TO CANCEL AN ORDER
######################################################################
@api.route("/orders/<int:order_id>/cancel", strict_slashes=False)
class CancelOrderResource(Resource):
    """Cancel an Order"""

    @api.marshal_with(order_model)
    def put(self, order_id):
        """Action route to cancel an order using order id"""
        app.logger.info(f"Request to cancel order id:{order_id}")
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )
        app.logger.info(
            f"Changing status of order with order id:{order_id} to CANCELLED"
        )
        order.status = OrderStatus.CANCELLED
        order.update()
        return order.serialize(), status.HTTP_200_OK


######################################################################
#  ACTION ROUTE TO UPDATE ORDER STATUS
######################################################################
@api.route("/orders/<int:order_id>/update", strict_slashes=False)
class UpdateStatusResource(Resource):
    """Update the status of an Order"""

    def put(self, order_id):
        """Action to update the status of an order"""
        app.logger.info(f"Request to change status of order id:{order_id}")
        # Check if order exists
        order = Order.find(order_id)

        if not order:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )

        if not order.items:
            abort(
                status.HTTP_400_BAD_REQUEST,
                f"Cannot change status of order_id:{order_id} with no items",
            )

        if order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Cannot change the status of an order that is COMPLETED or CANCELLED",
            )
        # Get the next status
        status_list = OrderStatus.list()
        current_status_idx = status_list.index(order.status.value)

        # Change the status to the next one
        next_status = OrderStatus(status_list[current_status_idx + 1])
        order.status = next_status
        order.update()  # Save the updated order status to the database
        return {"order_id": order.id, "status": order.status.value}, status.HTTP_200_OK


######################################################################
#  R E S T   A P I   E N D P O I N T S  F O R  I T E M S
######################################################################


######################################################################
#  LIST/CREATE ITEMS FROM AN EXISTING ORDER
######################################################################
@api.route("/orders/<int:order_id>/items", strict_slashes=False)
class ItemCollection(Resource):
    """Item Operations"""

    @api.marshal_list_with(item_model)
    def get(self, order_id):
        """
        List Items in an Order
        This endpoint returns all Items for an Order
        """
        app.logger.info(f"Request to list Items for Order with id: {order_id}")

        # Check if order exists
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )

        # Get items for the order
        items = order.items
        results = [item.serialize() for item in items]

        app.logger.info(f"Returning {len(results)} items for Order {order_id}")
        return results, status.HTTP_200_OK

    @api.expect(item_model)
    @api.marshal_with(item_model, code=201)
    def post(self, order_id):
        """
        Create an Item on an Order

        This endpoint will add an item to an order
        """
        app.logger.info("Request to create an Item for Order with id: %s", order_id)
        check_content_type("application/json")
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )

        # Create an item from the json data
        item = Item()
        item.deserialize(api.payload)

        # Append the item to the order
        order.items.append(item)
        order.update()

        # Prepare a message to return
        message = item.serialize()

        # Send the location to GET the new item
        location_url = url_for(
            "item_resource", order_id=item.order_id, item_id=item.id, _external=True
        )
        return message, status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  RETRIEVE AN ITEM FROM AN EXISTING ORDER
######################################################################
@api.route("/orders/<int:order_id>/items/<int:item_id>", strict_slashes=False)
class ItemResource(Resource):
    """Item Operations"""

    @api.marshal_with(item_model)
    def get(self, order_id, item_id):
        """
        Get an Item from an Order

        This endpoint returns just an item
        """
        app.logger.info(
            "Request to retrieve Item %s for Order id: %s", (item_id, order_id)
        )

        # See if the item exists and abort if it doesn't
        item = Item.find(item_id)
        if not item or item.order_id != order_id:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' in Order '{order_id}' could not be found.",
            )

        return item.serialize(), status.HTTP_200_OK

    @api.expect(item_model)
    @api.marshal_with(item_model)
    def put(self, order_id, item_id):
        """
        Update an Item in an Order

        This endpoint will update an Item based on the body that is posted
        """
        app.logger.info("Request to update Item %s for Order id: %s", item_id, order_id)
        check_content_type("application/json")

        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' could not be found.",
            )

        item = Item.find(item_id)
        if not item or item.order_id != order_id:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' in Order '{order_id}' could not be found.",
            )

        item.deserialize(api.payload)

        item.id = item_id
        item.order_id = order_id

        item.update()

        return item.serialize(), status.HTTP_200_OK

    def delete(self, order_id, item_id):
        """Delete an item from a given order"""
        app.logger.info(
            "Request to delete an item '%s' from Order with id: %s", (item_id, order_id)
        )

        # check for order
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with order id: '{order_id}' could not be found.",
            )
        # Check if item is there
        item = Item.find(item_id)
        if item:
            item.delete()
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  A L L    R O U T E S     C O M P L E T E
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {content_type}"
    )


# route to trigger 500 internal server error
@app.route("/500_error")
def server_error():
    """Triggers server error"""
    app.logger.info("Triggering 500_INTERNAL_SERVER_ERROR.")
    abort(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Testing 500_INTERNAL_SERVER_ERROR",
    )
