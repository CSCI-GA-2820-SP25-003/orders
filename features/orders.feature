Feature: The order service back-end
  As a manager
  I need a RESTful catalog service
  So that I can keep track of all orders

Background:
    Given the following orders
        | customer_name  | status    | product_name  | quantity | price   |
        | Customer One   | CREATED   | T-Shirt       | 2        | 99.99   |
        | Customer Two   | SHIPPED   | Phone         | 1        | 429.99  |
        | Customer Three | CANCELLED | Macbook       | 1        | 999.99  |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Order Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: The server is running
    When I visit the "Health Page"
    Then I should see "Healthy" in the health page
    And I should not see "404 Not Found"

Scenario: Query Orders by Various Criteria
    When I visit the "Home Page"
    And I press the "Clear" button
    # Test filtering by customer name
    When I set the "Customer Name" to "Customer One"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Customer One" in the results
    And I should not see "Customer Two" in the results
    And I should not see "Customer Three" in the results
    
    # Test filtering by status
    When I press the "Clear" button
    And I select "SHIPPED" in the "Status" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Customer Two" in the results
    And I should not see "Customer One" in the results
    And I should not see "Customer Three" in the results
    
    # Test filtering by product name
    When I press the "Clear" button
    And I set the "Product Name" to "Macbook"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Customer Three" in the results
    And I should not see "Customer One" in the results
    And I should not see "Customer Two" in the results
    
    # Test combined filters
    When I press the "Clear" button
    And I set the "Customer Name" to "Customer Three"
    And I select "CANCELLED" in the "Status" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Customer Three" in the results
    And I should see "CANCELLED" in the results
    And I should not see "Customer One" in the results
    And I should not see "Customer Two" in the results

Scenario: Update an Order
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Order ID" field
    And I press the "Clear" button
    And I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    When I set the "Customer Name" to "John Doe"
    And I select "SHIPPED" in the "Status" dropdown
    And I set the "Product Name" to "Laptop"
    And I set the "Quantity" to "1"
    And I set the "Price" to "1299.99"
    And I press the "Update" button
    Then I should see the message "Success"
    When I press the "Clear" button
    And I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "John Doe" in the "Customer Name" field
    And I should see "SHIPPED" in the "Status" field
    And I should see "T-Shirt" in the "Product Name" field
    And I should see "2" in the "Quantity" field
    And I should see "99.99" in the "Price" field

Scenario: Update an Item
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Order ID" field
    And I paste the "ID Item" field 
    And I press the "Search Item" button
    Then I should see the message "Success"
    Then I should see "99.99" in the "Item Price" field
    When I set the "Item Price" to "600"
    And I press the "Update Item" button
    Then I should see the message "Success"
    When I press the "Clear Item" button
    And I copy the "Order ID" field
    And I paste the "ID Item" field
    And I press the "Search Item" button
    Then I should see "600" in the "Item Price" field

Scenario: Cancel an Order
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Order ID" field
    And I press the "Clear" button
    And I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Customer One" in the "Customer Name" field
    And I should see "CREATED" in the "Status" field
    When I press the "Cancel" button
    Then I should see the message "Success"
    And I should see "CANCELLED" in the "Status" field
    When I press the "Clear" button
    And I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "CANCELLED" in the "Status" field

Scenario: Read an Order
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Order ID" field
    And I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Customer One" in the "Customer Name" field
    And I should see "CREATED" in the "Status" field