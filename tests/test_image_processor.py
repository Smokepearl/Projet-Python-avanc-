"""Tests unitaires du traitement d'images (sans réseau, images synthétiques)."""

import os
import sys
import tempfile
import unittest

from PIL import Image

# Permet d'exécuter ce fichier directement ou via « python -m unittest ».
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import image_processor as ip


class TestImageProcessor(unittest.TestCase):
    def setUp(self):
        self.base = Image.new("RGB", (600, 800), color=(200, 100, 50))

    def test_crop_and_resize(self):
        out = ip.crop_and_resize(self.base, crop_factor=0.5, resize_to=(100, 120))
        self.assertEqual(out.size, (100, 120))

    def test_load_logo_bw_is_grayscale(self):
        with tempfile.TemporaryDirectory() as tmp:
            logo_path = os.path.join(tmp, "logo.png")
            Image.new("RGB", (50, 50), color=(10, 20, 30)).save(logo_path)
            logo = ip.load_logo_bw(logo_path)
            self.assertEqual(logo.mode, "L")  # niveaux de gris (N&B)

    def test_load_logo_missing_raises(self):
        with self.assertRaises(ip.ImageProcessingError):
            ip.load_logo_bw("chemin/inexistant/logo.png")

    def test_rotate_and_paste_logo_keeps_size_and_mode(self):
        logo = Image.new("L", (40, 40), color=0)
        photo = ip.rotate_and_paste_logo(self.base, logo, angle=45)
        self.assertEqual(photo.size, self.base.size)  # taille de base conservée
        self.assertEqual(photo.mode, "RGB")
        # L'original ne doit pas être modifié (copie défensive).
        self.assertEqual(self.base.getpixel((0, 0)), (200, 100, 50))


if __name__ == "__main__":
    unittest.main()
