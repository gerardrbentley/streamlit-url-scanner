import pytest
from selenium.webdriver.common.by import By
from seleniumbase import BaseCase


class VisualTest(BaseCase):
    @pytest.mark.e2e
    def test_app_runs(self):
        # automated visual regression testing
        # tests page has identical structure to baseline
        # https://github.com/seleniumbase/SeleniumBase/tree/master/examples/visual_testing
        self.open("http://localhost:8501")
        self.assert_element("#url-scan")
        self.check_window(name="app_runs", level=3)

    @pytest.mark.e2e
    def test_app_detects_urls(self):
        self.open("http://localhost:8501")

        self.wait_for_element("[data-testid=stFileUploader]")
        self.execute_script(
            """document.querySelector('input[type="file"]').style.display='block'"""
        )
        self.choose_file(
            'input[type="file"]',
            "samples/sample_urls.jpg",
            by=By.CSS_SELECTOR,
            timeout=20,
        )
        self.assert_element("#extracted-urls")
        self.wait_for_element(".streamlit-expanderHeader")
        self.check_window(name="app_detects_urls", level=3)
