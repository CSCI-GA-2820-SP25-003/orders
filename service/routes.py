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
Order Service with Swagger

This service implements a REST API that allows you to Create, Read, Update
and Delete Order
"""

from flask import current_app as app  # Import Flask application
from flask_restx import Resource, fields, reqparse, Api
from service.models import Order, Item, OrderStatus
from service.common import status  # HTTP Status Codes

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Order Demo REST API Swagger Service",
    description="This is a Order server.",
    default="orders",
    default_label="Order service operations",
    doc="/apidocs",  # default also could use doc='/apidocs/'
    prefix="/api",
)


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return {"message": "Healthy"}, status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file("index.html")


# Define the model so that the docs reflect what can be sent
base_item_model = api.model(
    "Item",
    {
        "name": fields.String(description="The name of the product"),
        "quantity": fields.Integer(description="Quantity of item"),
        # pylint: disable=protected-access
        "price": fields.Float(description="Price of quantity of item"),
    },
)

item_model = api.inherit(
    "ItemModel",
    base_item_model,
    {
        "id": fields.Integer(
            readOnly=True,
            required=True,
            description="The unique id assigned internally by service",
        ),
        "order_id": fields.Integer(
            readOnly=True,
            required=True,
            description="The unique order id assigned internally by service",
        ),
    },
)

# Define the model so that the docs reflect what can be sent
base_order_model = api.model(
    "Order",
    {
        "customer_name": fields.String(
            required=True, description="The name of the customer"
        ),
        "status": fields.String(
            required=True,
            enum=OrderStatus._member_names_,
            description="Status of the order",
        ),
        # pylint: disable=protected-access
    },
)

order_model = api.inherit(
    "OrderModel",
    base_order_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        ),
        "items": fields.List(
            fields.Nested(item_model), description="The list of items in the Order"
        ),
    },
)

# query string arguments: customer_name, order_status and product_name
order_args = reqparse.RequestParser()
order_args.add_argument(
    "customer_name",
    type=str,
    location="args",
    required=False,
    help="List orders by customer name",
)
order_args.add_argument(
    "status",
    type=str,
    location="args",
    required=False,
    help="List orders by status",
)
order_args.add_argument(
    "product_name",
    type=str,
    location="args",
    required=False,
    help="List orders by product_name in items",
)
order_args.add_argument(
    "order_id",
    type=int,
    location="args",
    required=False,
    help="List orders by order_id",
)


######################################################################
# PATH: /orders/<order_id>
######################################################################
@api.route("/orders/<int:order_id>")
@api.param("order_id", "The order identifier")
class OrderResource(Resource):
    """
    OrderResource class

    Allows the manipulation of a single Order
    GET /order{id} - Retrieve an Order with the id
    PUT /order{id} - Update an Order with the id
    DELETE /order{id} -  Deletes an Order with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE AN ORDER
    # ------------------------------------------------------------------
    @api.doc("retrieve_order")
    @api.response(200, "Success")
    @api.response(404, "Order not found")
    @api.marshal_with(order_model)
    def get(self, order_id):
        """Retrieve an Order given its order_id"""
        app.logger.info("Request for Order with id: %s", order_id)

        # Get the order, if it exists
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )

        return order.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING ORDER
    # ------------------------------------------------------------------
    @api.doc("update_order")
    @api.response(200, "Success")
    @api.response(404, "Order not found")
    @api.expect(base_order_model)
    @api.marshal_with(order_model)
    def put(self, order_id):
        """Update an Order given its order_id"""
        app.logger.info("Request to update Order with id: %s", order_id)

        # Get the order, if it exists
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )

        # Update the order with the data in the body
        data = api.payload
        app.logger.debug("Payload received for update: %s", data)
        order.deserialize(data)
        order.id = order_id
        order.update()

        return order.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE AN ORDER
    # ------------------------------------------------------------------
    @api.doc("delete_order")
    @api.response(204, "No Content")
    def delete(self, order_id):
        """Delete an Order given its order_id"""
        app.logger.info("Request to delete Order with id: %s", order_id)

        # Get the order, if it exists
        order = Order.find(order_id)
        if order:
            order.delete()

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#   PATH: /orders
######################################################################
@api.route("/orders", strict_slashes=False)
class OrderCollection(Resource):
    """
    OrderCollection class

    Allows the manipulation of a collection of Orders
    GET /orders - List Orders based on query
    POST /orders - Create an Order
    """

    # ------------------------------------------------------------------
    # LIST ORDERS
    # ------------------------------------------------------------------
    @api.doc("list_orders")
    @api.expect(order_args, validate=True)
    @api.response(200, "Success")
    @api.marshal_list_with(order_model)
    def get(self):
        """List all Orders"""
        app.logger.info("Request to list Orders...")

        # Get query parameters
        args = order_args.parse_args()
        customer_name = args["customer_name"]
        order_status = args["status"]
        product_name = args["product_name"]
        order_id = args["order_id"]

        # Get all orders
        filtered_orders = Order.find_by_filters(
            customer_name=customer_name,
            order_status=order_status,
            order_id=order_id,
            product_name=product_name,
        )

        app.logger.info(
            f"After filtering: {len(filtered_orders)} orders match criteria"
        )

        # Create response
        results = [order.serialize() for order in filtered_orders]

        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # CREATE A NEW ORDER
    # ------------------------------------------------------------------
    @api.doc("create_order")
    @api.response(201, "Order Created")
    @api.expect(base_order_model)
    @api.marshal_with(order_model, code=201)
    def post(self):
        """Creates an Order"""
        app.logger.info("Request to create an Order")
        # Create the order
        order = Order()
        order.deserialize(api.payload)
        order.create()

        # Create a message to return
        message = order.serialize()
        location_url = api.url_for(OrderResource, order_id=order.id, _external=True)

        return message, status.HTTP_201_CREATED, {"Location": location_url}


#######################################################################
#   PATH: /orders/<order_id>/cancel
#######################################################################
@api.route("/orders/<int:order_id>/cancel")
@api.param("order_id", "The order identifier")
class OrderCancelResource(Resource):
    """Cancel Action for an Order"""

    @api.doc("cancel_order")
    @api.response(200, "Success")
    @api.response(404, "Order not found")
    @api.marshal_with(order_model)
    def put(self, order_id):
        """Cancel an Order given its order_id"""
        app.logger.info("Request to cancel Order with id: %s", order_id)

        # Get the order, if it exists
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )

        # Change the status to CANCELLED
        app.logger.info(f"Changing status of order with id:{order_id} to CANCELLED")
        order.status = OrderStatus.CANCELLED
        order.update()

        return order.serialize(), status.HTTP_200_OK


######################################################################
#   PATH: /orders/<order_id>/update
######################################################################
@api.route("/orders/<int:order_id>/update")
@api.param("order_id", "The order identifier")
class OrderUpdateResource(Resource):
    """Update Action for an Order"""

    @api.doc("update_order_status")
    @api.response(200, "OK")
    @api.response(400, "Bad Request")
    @api.response(404, "Order not found")
    @api.marshal_with(order_model)
    def put(self, order_id):
        """Update an Order given its order_id"""
        app.logger.info("Request to update Order with id: %s", order_id)

        # Get the order, if it exists
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )

        # Check if there are items in the order
        if not order.items:
            abort(
                status.HTTP_400_BAD_REQUEST,
                f"Cannot change status of order_id:{order_id} with no items",
            )

        # Check if the order is already COMPLETED or CANCELLED
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
        order.update()

        return {"order_id": order.id, "status": order.status.value}, status.HTTP_200_OK


#######################################################################
#   PATH: /orders/<order_id>/items
########################################################################
@api.route("/orders/<int:order_id>/items")
@api.param("order_id", "The order identifier")
class OrderItemCollection(Resource):
    """
    OrderItemCollection class

    Allows the manipulation of a collection of Items
    GET /orders/{order_id}/items - List Items in an Order with order_id
    POST /orders/{order_id}/items - Create an Item on an Order with order_id
    """

    # ------------------------------------------------------------------
    # LIST ITEMS IN AN ORDER
    # ------------------------------------------------------------------
    @api.doc("list_items")
    @api.response(200, "Success")
    @api.response(404, "Order not found")
    @api.marshal_list_with(item_model)
    def get(self, order_id):
        """List all Items in an Order"""
        app.logger.info("Request to list Items for Order with id: %s", order_id)

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

    # ------------------------------------------------------------------
    # CREATE AN ITEM IN AN ORDER
    # ------------------------------------------------------------------
    @api.doc("create_item")
    @api.response(201, "Item Created")
    @api.response(404, "Order not found")
    @api.response(400, "Bad Request")
    @api.expect(base_item_model)
    @api.marshal_with(item_model, code=201)
    def post(self, order_id):
        """Creates an Item on an Order"""
        app.logger.info("Request to create an Item for Order with id: %s", order_id)

        # See if the order exists and abort if it doesn't
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' could not be found.",
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
        location_url = api.url_for(
            ItemResource, order_id=item.order_id, item_id=item.id, _external=True
        )
        return message, status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#   PATH: /orders/<order_id>/items/<item_id>
######################################################################
@api.route("/orders/<int:order_id>/items/<int:item_id>")
@api.param("order_id", "The order identifier")
@api.param("item_id", "The item identifier")
class ItemResource(Resource):
    """
    ItemResource class

    Allows the manipulation of a single Item
    GET /orders/{order_id}/items/{item_id} - Retrieve an Item with the id
    PUT /orders/{order_id}/items/{item_id} - Update an Item with the id
    DELETE /orders/{order_id}/items/{item_id} -  Deletes an Item with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE AN ITEM IN ORDER
    # ------------------------------------------------------------------
    @api.doc("retrieve_item")
    @api.response(200, "Success")
    @api.response(404, "Item not found")
    @api.marshal_with(item_model)
    def get(self, order_id, item_id):
        """Retrieve an Item given its item_id"""
        app.logger.info(
            "Request to retrieve Item %s for Order id: %s", item_id, order_id
        )

        # See if the item exists and abort if it doesn't
        item = Item.find(item_id)
        if not item or item.order_id != order_id:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' in Order '{order_id}' could not be found.",
            )

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN ITEM
    # ------------------------------------------------------------------
    @api.doc("update_item")
    @api.response(200, "Success")
    @api.response(404, "Item not found")
    @api.response(404, "Order not found")
    @api.expect(item_model)
    @api.marshal_with(item_model)
    def put(self, order_id, item_id):
        """Update an Item given its item_id"""
        app.logger.info("Request to update Item %s for Order id: %s", item_id, order_id)

        # See if the order exists and abort if it doesn't
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' could not be found.",
            )

        # See if the item exists and abort if it doesn't
        item = Item.find(item_id)
        if not item or item.order_id != order_id:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' in Order '{order_id}' could not be found.",
            )

        # Update item with info in the json request
        data = api.payload
        item.deserialize(data)
        item.id = item_id
        if item:
            Item.update(item)
        # Return the updated order
        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE AN ITEM
    # ------------------------------------------------------------------
    @api.doc("delete_item")
    @api.response(204, "No Content")
    @api.response(404, "Order not found")
    def delete(self, order_id, item_id):
        """Delete an Item given its item_id"""
        app.logger.info("Request to delete Item %s for Order id: %s", item_id, order_id)

        # See if the order exists and abort if it doesn't
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' could not be found.",
            )

        # Check if item is there
        item = Item.find(item_id)
        if item:
            item.delete()

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /500_error
######################################################################
@api.route("/500_error", strict_slashes=False)
class ServerErrorResource(Resource):
    """Test server error"""

    @api.doc("server_error")
    @api.response(500, "Internal Server Error")
    def get(self):
        """Trigger a 500 Internal Server Error"""
        app.logger.info("Triggering 500_INTERNAL_SERVER_ERROR.")
        abort(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Testing 500_INTERNAL_SERVER_ERROR",
        )


######################################################################
# U T I L I T Y     F U N C T I O N S
######################################################################
def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)
