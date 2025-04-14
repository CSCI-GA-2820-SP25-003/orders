$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#order_order_id").val(res.id);
        $("#order_customer_name").val(res.customer_name);
        $("#order_status").val(res.status);

        // Handle items array - taking first item for now
        if (res.items && res.items.length > 0) {
            let item = res.items[0];
            $("#order_product_name").val(item.product_name);
            $("#order_price").val(item.price);
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#order_order_id").val("");
        $("#order_customer_name").val("");
        $("#order_status").val("");
        $("#order_product_name").val("");
        $("#order_price").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create an Order
    // ****************************************

    $("#create-btn").click(function () {
        let customer_name = $("#order_customer_name").val();
        let status = $("#order_status").val();
        let product_name = $("#order_product_name").val();
        let quantity = $("#order_quantity").val();
        let price = $("#order_price").val();

        let data = {
            "customer_name": customer_name,
            "status": status,
            "items": [{
                "name": product_name,
                "quantity": parseInt(quantity),
                "price": parseFloat(price)
            }]
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/orders",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update an Order
    // ****************************************

    $("#update-btn").click(function () {
        let order_id = $("#order_id").val();
        let customer_name = $("#order_customer_name").val();
        let status = $("#order_status").val();
        let product_name = $("#order_product_name").val();
        let quantity = $("#order_quantity").val();
        let price = $("#order_price").val();

        let data = {
            "customer_name": customer_name,
            "status": status,
            "items": [{
                "name": product_name,
                "quantity": parseInt(quantity),
                "price": parseFloat(price)
            }]
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Retrieve an Order
    // ****************************************

    $("#retrieve-btn").click(function () {

        let order_id = $("#order_order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete an Order
    // ****************************************

    $("#delete-btn").click(function () {

        let order_id = $("#order_order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Pet has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#order_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for an Order
    // ****************************************

    $("#search-btn").click(function () {
        let order_id = $("#order_order_id").val();
        let customer_name = $("#order_customer_name").val();
        let status = $("#order_status").val();
        let product_name = $("#order_product_name").val();

        let queryString = ""

        if (order_id) {
            queryString += 'order_id=' + order_id
        }
        if (customer_name) {
            queryString += 'customer_name=' + customer_name
        }
        if (status) {
            if (queryString.length > 0) {
                queryString += '&' + status
            } else {
                queryString += 'status=' + status
            }
        }
        if (product_name) {
            if (queryString.length > 0) {
                queryString += '&';
            }
            queryString += 'product_name=' + product_name;
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/orders?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Customer Name</th>'
            table += '<th class="col-md-2">Product Name</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '<th class="col-md-2">Price</th>'
            table += '<th class="col-md-2">Status</th>'
            table += '</tr></thead><tbody>'
            let firstOrder = "";
            for(let i = 0; i < res.orders.length; i++) {
                let order = res.orders[i];
                let item = order.items[0] || {}; // Get first item or empty object if no items
                table +=  `<tr id="row_${i}"><td>${order.id}</td><td>${order.customer_name}</td><td>${item.name || ''}</td><td>${item.quantity}</td><td>${item.price || ''}</td><td>${order.status}</td></tr>`;
                if (i == 0) {
                    firstOrder = order;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstOrder != "") {
                update_form_data(firstOrder)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
