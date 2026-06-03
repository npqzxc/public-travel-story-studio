from io import BytesIO
import unittest

from app.http import extract_filters, parse_form


class HttpTests(unittest.TestCase):
    def test_parse_form_reads_urlencoded_body(self):
        environ = {
            "CONTENT_LENGTH": "27",
            "wsgi.input": BytesIO(b"title=Hello&priority=urgent"),
        }
        parsed = parse_form(environ)
        self.assertEqual(parsed["title"], "Hello")
        self.assertEqual(parsed["priority"], "urgent")

    def test_extract_filters_skips_blank_values(self):
        environ = {"QUERY_STRING": "status=blocked&query=&assignee=yuki"}
        filters = extract_filters(environ)
        self.assertEqual(filters, {"status": "blocked", "assignee": "yuki"})


if __name__ == "__main__":
  unittest.main()
