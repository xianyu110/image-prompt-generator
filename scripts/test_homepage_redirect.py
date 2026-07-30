from html.parser import HTMLParser
from pathlib import Path
import unittest


TARGET_URL = "https://gptimage2.asia/generate"
STYLE_CACHE_VERSION = "20260730-generator-redirect"
SCRIPT_CACHE_VERSION = "20260730-try-without-generate"


class GenerateControlParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.generate_href = None
        self.has_submit_button = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()
        if "generate-button" not in classes:
            return
        if tag == "a":
            self.generate_href = attributes.get("href")
        if tag == "button" and attributes.get("type", "submit") == "submit":
            self.has_submit_button = True


class HomepageRedirectTest(unittest.TestCase):
    def test_generate_control_is_cache_safe_link(self):
        html = (Path(__file__).parents[1] / "index.html").read_text()
        parser = GenerateControlParser()
        parser.feed(html)

        self.assertEqual(parser.generate_href, TARGET_URL)
        self.assertFalse(parser.has_submit_button)
        self.assertIn(f"styles.css?v={STYLE_CACHE_VERSION}", html)
        self.assertIn(f"script.js?v={SCRIPT_CACHE_VERSION}", html)

    def test_try_prompt_does_not_generate_automatically(self):
        script = (Path(__file__).parents[1] / "script.js").read_text()
        try_prompt = script.split("async function tryPrompt(item) {", 1)[1].split(
            "\n}\n\nfunction buildLocalPrompt", 1
        )[0]

        self.assertNotIn("generatePrompt(", try_prompt)


if __name__ == "__main__":
    unittest.main()
