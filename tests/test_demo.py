import unittest
from demo import display_visible

PKG = 'com.android.settings'
TOOLBAR = 'com.android.settings:id/collapsing_toolbar'

def tree(title, control, *, package=PKG, desc=True, toolbar=TOOLBAR):
    attr = 'content-desc' if desc else 'text'
    return (f'<hierarchy><node package="{package}" resource-id="{toolbar}" {attr}="{title}"/>'
            f'<node package="{package}" text="{control}"/></hierarchy>')

class OracleTests(unittest.TestCase):
    def test_android_34_observed_accessibility_title(self):
        self.assertTrue(display_visible(tree('Display', 'Brightness level')))

    def test_title_as_text(self):
        self.assertTrue(display_visible(tree('Display', 'Screen timeout', desc=False)))

    def test_settings_list_is_not_display(self):
        self.assertFalse(display_visible(tree('Settings', 'Display')))

    def test_unrelated_screen(self):
        self.assertFalse(display_visible(tree('Other', 'Dark theme')))

    def test_wrong_package_cannot_pass(self):
        self.assertFalse(display_visible(tree('Display', 'Brightness level', package='example.other')))

    def test_generic_display_label_cannot_pass(self):
        self.assertFalse(display_visible(tree('Display', 'Brightness level', toolbar='android:id/title')))

    def test_title_without_display_controls_cannot_pass(self):
        self.assertFalse(display_visible(tree('Display', 'Network')))
