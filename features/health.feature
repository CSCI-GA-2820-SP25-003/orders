Feature: Service Health Check
  As a manager
  I need to make sure the service is healthy
  So that I can ensure the order service is operational

  Background:
    Given the server is started

  Scenario: The server is running
    When I visit the "health page"
    Then I should see "Healthy"
    And I should not see "404 Not Found"
