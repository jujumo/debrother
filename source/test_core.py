import unittest
from core import *
import os.path as path


class TestSorting(unittest.TestCase):
    def setUp(self):
        self._samples = sort_lexicographical([
            'C:\\scan\\test\\Numérisation_20190527 (2).jpg',
            'C:\\scan\\test\\Numérisation_20190527.jpg',
            'C:\\scan\\test\\Numérisation_20190527_10 (2).jpg',
            'C:\\scan\\test\\Numérisation_20190527_10.jpg',
            'C:\\scan\\test\\Numérisation_20190527_2 (2).jpg',
            'C:\\scan\\test\\Numérisation_20190527_2.jpg',
            'C:\\scan\\test\\Numérisation_20190527_3 (2).jpg',
            'C:\\scan\\test\\Numérisation_20190527_3.jpg',
            'C:\\scan\\test\\Numérisation_20190527_4 (2).jpg',
            'C:\\scan\\test\\Numérisation_20190527_4.jpg',
            'C:\\scan\\test\\Numérisation_20190527_5 (2).jpg',
            'C:\\scan\\test\\Numérisation_20190527_5.jpg',
            'C:\\scan\\test\\Numérisation_20190527_6 (2).jpg',
            'C:\\scan\\test\\Numérisation_20190527_6.jpg',
            'C:\\scan\\test\\Numérisation_20190527_7 (2).jpg',
            'C:\\scan\\test\\Numérisation_20190527_7.jpg',
            'C:\\scan\\test\\Numérisation_20190527_8 (2).jpg',
            'C:\\scan\\test\\Numérisation_20190527_8.jpg',
            'C:\\scan\\test\\Numérisation_20190527_9 (2).jpg',
            'C:\\scan\\test\\Numérisation_20190527_9.jpg'
        ])

    def test_numbering(self):
        result = self._samples
        result = sort_brother_numbering(result)
        self.assertEqual('C:\\scan\\test\\Numérisation_20190527 (2).jpg', result[0])
        self.assertEqual('C:\\scan\\test\\Numérisation_20190527_10.jpg', result[-1])

    def test_flip(self):
        result = self._samples
        result = sort_flip_recto_verso(result)
        self.assertListEqual(result[::2], self._samples[1::2])
        self.assertListEqual(result[1::2], self._samples[::2])

    def test_backward_verso(self):
        result = self._samples
        result = sort_backward_verso(result)
        self.assertListEqual(result[::2], self._samples[::2])
        self.assertListEqual(result[1::2], list(reversed(self._samples[1::2])))


if __name__ == '__main__':
    unittest.main()
