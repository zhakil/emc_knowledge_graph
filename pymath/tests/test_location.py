import unittest

from pymath.lib.location import Location


class TestLocation(unittest.TestCase):

    def test_location_creation(self):
        loc = Location("path/to/file.py", 10, 5)
        self.assertEqual(loc.path, "path/to/file.py")
        self.assertEqual(loc.line, 10)
        self.assertEqual(loc.column, 5)

    def test_location_equality(self):
        loc1 = Location("path/to/file.py", 10, 5)
        loc2 = Location("path/to/file.py", 10, 5)
        loc3 = Location("path/to/other_file.py", 10, 5)
        loc4 = Location("path/to/file.py", 11, 5)
        loc5 = Location("path/to/file.py", 10, 6)

        self.assertEqual(loc1, loc2)
        self.assertNotEqual(loc1, loc3)
        self.assertNotEqual(loc1, loc4)
        self.assertNotEqual(loc1, loc5)
        self.assertNotEqual(loc1, "not a location")

    def test_location_repr(self):
        loc = Location("path/to/file.py", 10, 5)
        self.assertEqual(repr(loc), "Location(path='path/to/file.py', line=10, column=5)")

    def test_location_str(self):
        loc = Location("path/to/file.py", 10, 5)
        self.assertEqual(str(loc), "path/to/file.py:10:5")

if __name__ == '__main__':
    unittest.main()
