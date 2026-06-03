import unittest

from app import auth


class AuthTests(unittest.TestCase):
    def test_round_trip_session_cookie(self):
        header_name, header_value = auth.build_session_cookie(7)
        self.assertEqual(header_name, "Set-Cookie")
        cookie_value = header_value.split(";", 1)[0]
        parsed_user_id = auth.get_session_user_id(cookie_value)
        self.assertEqual(parsed_user_id, 7)

    def test_tampered_cookie_is_rejected(self):
        valid = auth.create_session_value(3)
        tampered = valid[:-1] + ("0" if valid[-1] != "0" else "1")
        self.assertIsNone(auth.parse_session_value(tampered))


if __name__ == "__main__":
    unittest.main()
