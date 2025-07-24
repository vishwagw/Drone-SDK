class TestFramework:
    """Provides utilities for testing the SDK."""
    
    def __init__(self):
        self.test_results = []
        
    def assert_equal(self, actual, expected, message=""):
        """Assert that two values are equal."""
        if actual != expected:
            self.test_results.append(f"FAIL: {message} - Expected {expected}, got {actual}")
        else:
            self.test_results.append(f"PASS: {message}")
    
    def assert_true(self, condition, message=""):
        """Assert that a condition is true."""
        if not condition:
            self.test_results.append(f"FAIL: {message} - Condition is not true")
        else:
            self.test_results.append(f"PASS: {message}")
    
    def report(self):
        """Print the test results."""
        for result in self.test_results:
            print(result)
        self.test_results.clear()  # Clear results after reporting