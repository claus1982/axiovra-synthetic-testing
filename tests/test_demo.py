import unittest
from demo import display_visible

class OracleTests(unittest.TestCase):
    def test_display(self):
        self.assertTrue(display_visible('<hierarchy><node text="Display"/><node text="Brightness level"/></hierarchy>'))

    def test_settings_list_is_not_display(self):
        self.assertFalse(display_visible('<hierarchy><node text="Display"/><node text="Network"/></hierarchy>'))

    def test_unrelated_screen(self):
        self.assertFalse(display_visible('<hierarchy><node text="Dark theme"/></hierarchy>'))
