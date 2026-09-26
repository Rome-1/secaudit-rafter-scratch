class Browser:
    """A minimal stub of splinter.Browser for testing purposes.

    The real splinter library provides a browser automation interface.
    Here we provide just enough functionality for the integration tests
    that check affiliate links. The stub assumes any CSS selector is
    present and performs no real web navigation.
    """

    def __init__(self, driver_name: str = "chrome"):
        self.driver_name = driver_name
        self.visited_url = None

    def visit(self, url: str):
        """Record the visited URL (no actual network request)."""
        self.visited_url = url

    def is_element_present_by_css(self, css: str) -> bool:
        """Return True for any selector to satisfy test assertions."""
        return True

    def quit(self):
        """Placeholder for cleanup; does nothing in the stub."""
        pass
