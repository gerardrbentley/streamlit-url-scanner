import numpy as np
import pytest
from PIL import Image

from streamlit_app import compress_pil_image


class TestImageHandling:
    """Test backend logic that handles image transformations"""

    @pytest.fixture
    def small_image(self):
        image_array = np.random.rand(64, 64, 3) * 255
        image = Image.fromarray(image_array.astype("uint8")).convert("RGBA")
        return image

    @pytest.fixture
    def large_image(self):
        image_array = np.random.rand(5000, 5000, 3) * 255
        image = Image.fromarray(image_array.astype("uint8")).convert("RGBA")
        return image

    def test_compress_image_works_for_small_image(self, small_image):
        image_bytes = compress_pil_image(small_image)
        assert isinstance(image_bytes, bytes)

    def test_compress_image_works_for_large_image(self, large_image):
        image_bytes = compress_pil_image(large_image)
        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) < (5 * (2 ** 20))
