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
from service.models import Item, Order
from service.common import status  # HTTP Status Codes


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
    response_data = {
        "name": "Welcome to Orders Service",
        "version": "1.0.0",
        "list_resource_url": url_for("list_orders"),
    }
    return jsonify(response_data), status.HTTP_200_OK


######################################################################
#  R E S T   A P I   E N D P O I N T S  F O R  O R D E R S
######################################################################


# L I S T   A L L   O R D E R S #########
"""
curl -X GET "http://127.0.0.1:8080/orders"
"""


@app.route("/orders", methods=["GET"])
def list_orders():
    """
    List all Orders
    This endpoint returns a list of all Orders with optional filtering and pagination
    """
    app.logger.info("Request to list Orders...")

    # Get query parameters
    status_val = request.args.get("status")
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)

    # Get all orders
    orders = Order.all()
    app.logger.info(f"Found {len(orders)} total orders")

    # Filter orders manually to ensure correct status comparison
    filtered_orders = []

    for order in orders:
        # Only filter by status if a status filter was provided
        if status_val:
            # Get the order's status value as a string for comparison
            order_status = order.status
            order_status_val = (
                order_status.value
                if hasattr(order_status, "value")
                else str(order_status)
            )

            app.logger.info(
                f"Order {order.id}: status={order_status_val}, requested={status_val}"
            )

            # Skip this order if status doesn't match
            if order_status_val != status_val:
                continue

        # If we get here, add the order to our filtered list
        filtered_orders.append(order)

    app.logger.info(f"After filtering: {len(filtered_orders)} orders match criteria")

    # Apply pagination
    total_items = len(filtered_orders)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paged_orders = filtered_orders[start_idx:end_idx]

    # Calculate total pages
    total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 0

    # Create response
    results = [order.serialize() for order in paged_orders]

    response = {
        "orders": results,
        "metadata": {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
        },
    }

    app.logger.info(f"Returning {len(results)} orders")
    return jsonify(response), status.HTTP_200_OK


# C R E A T E   A   N E W   O R D E R #########
"""
curl -X POST "http://127.0.0.1:8080/orders" \
-H "Content-Type: application/json" \
-d '{"customer_name": "Alice", "status": "PENDING"}'
"""


@app.route("/orders", methods=["POST"])
def create_order():
    """
    Creates an Order
    This endpoint will create an Order based on the data in the body that is posted
    """
    app.logger.info("Request to create an Order")
    check_content_type("application/json")

    # create the order
    order = Order()
    order.deserialize(request.get_json())
    order.create()

    # create a message to return
    message = order.serialize()
    location_url = url_for("get_order", order_id=order.id, _external=True)

    return jsonify(message), status.HTTP_201_CREATED, {"location": location_url}


# R E T R E I V E   A N     O R D E R   U S I N G   O R D E R   I D #########
"""
curl -X GET "http://127.0.0.1:8080/orders/1"
"""


@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    """
    Retrieve a single Order
    """
    app.logger.info("Request for Order with id: %s", order_id)

    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    return jsonify(order.serialize()), status.HTTP_200_OK


# U P D A T E   A N    E X I S T I N G   O R D E R    U S I N G      O R D E R   I D #
"""
curl -X PUT "http://127.0.0.1:8080/orders/1" \
    -H "Content-Type: application/json" \
    -d '{"customer_name": "Alice", "status": "shipped"}'
"""


@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    """
    Update an Order

    This endpoint will update an Order based on the body that is posted
    """
    app.logger.info("Request to update order with id: %s", order_id)
    check_content_type("application/json")

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id '{order_id}' was not found.")

    # update from the json in the body of the request
    order.deserialize(request.get_json())
    order.id = order_id
    order.update()

    return jsonify(order.serialize()), status.HTTP_200_OK


# D E L E T E   A N     O R D E R    U S I N G      O R D E R   I D #########
@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    """Delete order using the order id"""
    app.logger.info("Request to delete an order with id: %s", order_id)

    # check for order
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with order id: '{order_id}' is not found and cannot be deleted",
        )
    order.delete()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  R E S T   A P I   E N D P O I N T S  F O R  I T E M S
######################################################################


#   L I S T     I T E M S     F R O M     A N   E X I S T I N G     O R D E R   #########
# curl -X GET "http://127.0.0.1:8080/orders/1/items"
@app.route("/orders/<int:order_id>/items", methods=["GET"])
def list_items(order_id):
    """
    List Items in an Order
    This endpoint returns all Items for an Order
    """
    app.logger.info(f"Request to list Items for Order with id: {order_id}")

    # Check if order exists
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    # Get items for the order
    items = order.items
    results = [item.serialize() for item in items]

    app.logger.info(f"Returning {len(results)} items for Order {order_id}")
    return jsonify(results), status.HTTP_200_OK


#   A D D     A N     I T E M     T O   A N     A N     E X I S T I N G     O R D E R   ##
"""
curl -X POST "http://127.0.0.1:8080/orders/1/items" \
-H "Content-Type: application/json" \
-d '{
    "name": "Laptop",
    "price": 1200.99,
    "quantity": 10
    }'
"""


@app.route("/orders/<int:order_id>/items", methods=["POST"])
def create_item(order_id):
    """
    Create an Item on an Order

    This endpoint will add an item to an order
    """
    app.logger.info("Request to create an Item for Order with id: %s", order_id)
    check_content_type("application/json")

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' could not be found.",
        )

    # Create an item from the json data
    item = Item()
    item.deserialize(request.get_json())

    # Append the item to the order
    order.items.append(item)
    order.update()

    # Prepare a message to return
    message = item.serialize()

    # Send the location to GET the new item
    location_url = url_for(
        "get_item", order_id=item.order_id, item_id=item.id, _external=True
    )
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


#  R E T R E I V E    A N     I T E M     F R O M     A N      E X I S T I N G     O R D E R   #########
"""
curl -X GET "http://127.0.0.1:8080/orders/1/items/1"
"""


@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["GET"])
def get_item(order_id, item_id):
    """
    Get an Item from an Order

    This endpoint returns just an item
    """
    app.logger.info("Request to retrieve Item %s for Order id: %s", (item_id, order_id))

    # See if the item exists and abort if it doesn't
    item = Item.find(item_id)
    if not item or item.order_id != order_id:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' in Order '{order_id}' could not be found.",
        )

    return jsonify(item.serialize()), status.HTTP_200_OK


#   U P D A T E     A N     I T E M     F R O M     A N     E X I S T I N G     O R D E R   #########
"""
curl -X PUT "http://127.0.0.1:8080/orders/1/items/2" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "Updated Laptop",
           "price": 999.99,
           "quantity": 5
         }'
"""


@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["PUT"])
def update_item(order_id, item_id):
    """
    Update an Item in an Order

    This endpoint will update an Item based on the body that is posted
    """
    app.logger.info("Request to update Item %s for Order id: %s", item_id, order_id)
    check_content_type("application/json")

    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' could not be found."
        )

    item = Item.find(item_id)
    if not item or item.order_id != order_id:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' in Order '{order_id}' could not be found.",
        )

    item.deserialize(request.get_json())

    item.id = item_id
    item.order_id = order_id

    item.update()

    return jsonify(item.serialize()), status.HTTP_200_OK


#   D E L E T E     A N     I T E M     F R O M     A N     E X I S T I N G     O R D E R   #########
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
def delete_item_from_order(order_id, item_id):
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
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' in Order '{order_id}' could not be found.",
        )

    item.delete()
    return "", status.HTTP_204_NO_CONTENT


# R O U T E S     C O M P L E T E ################################


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
