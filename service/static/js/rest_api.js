$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#order_id").val(res.id);
        $("#order_customer_name").val(res.customer_name);
        $("#order_status").val(res.status);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#order_customer_name").val("");
        $("#order_status").val("PLACEHOLDER");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Pet
    // ****************************************

    $("#create-btn").click(function () {

        let customer_name = $("#order_customer_name").val();
        let status = $("#order_status").val();

        let data = {
            "customer_name": customer_name,
            "status": status
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
    // Update a Pet
    // ****************************************

    $("#update-btn").click(function () {

        let order_id = $("#order_id").val();
        let customer_name = $("#order_customer_name").val();
        let status = $("#order_status").val();

        let data = {
            "customer_name": customer_name,
            "status": status
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/orders/${order_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Pet
    // ****************************************

    $("#retrieve-btn").click(function () {

        let order_id = $("#order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: ''
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
    // Delete a Pet
    // ****************************************

    $("#delete-btn").click(function () {

        let order_id = $("#order_id").val();

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

        let customer_name = $("#order_customer_name").val();
        let status = $("#order_status").val();

        if (status == "UNKNOWN") status = null

        let queryString = ""

        if (customer_name) {
            queryString += 'customer_name=' + customer_name
        }
        if (status) {
            if (queryString.length > 0) {
                queryString += '&status=' + status
            } else {
                queryString += 'status=' + status
            }
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
            table += '<th class="col-md-2">Status</th>'
            table += '</tr></thead><tbody>'
            let firstOrder = "";
            for(let i = 0; i < res.orders.length; i++) {
                let order = res.orders[i];
                table +=  `<tr id="row_${i}"><td>${order.id}</td><td>${order.customer_name}</td><td>${order.status}</td></tr>`;
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
