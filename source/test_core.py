import unittest
from core import *


class TestSorting(unittest.TestCase):
    def setUp(self):
        self._samples = [
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527 (2).jpg',
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527.jpg',
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527_10 (2).jpg',
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527_10.jpg',
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527_2 (2).jpg',
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527_2.jpg',
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527_3 (2).jpg',
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527_3.jpg',
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527_4 (2).jpg',
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527_4.jpg',
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527_5 (2).jpg',
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527_5.jpg',
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527_6 (2).jpg',
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527_6.jpg',
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527_7 (2).jpg',
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527_7.jpg',
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527_8 (2).jpg',
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527_8.jpg',
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527_9 (2).jpg',
            'C:\\Users\\jumo\\Desktop\\scan\\test\\Numérisation_20190527_9.jpg'
        ]

    def test_flip(self):
        result = sort_flip_sheets(self._samples)
        self.assertListEqual(result[::2], self._samples[1::2])
        self.assertListEqual(result[1::2], self._samples[::2])


if __name__ == '__main__':
    unittest.main()
