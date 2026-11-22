import os
import tempfile
import unittest

import app as auth_app


class AuthenticationTestCase(unittest.TestCase):

    def setUp(self):

        # Create a temporary database for testing
        self.db_fd, self.db_path = tempfile.mkstemp()

        auth_app.DATABASE = self.db_path
        auth_app.app.config["TESTING"] = True
        auth_app.app.config["SECRET_KEY"] = "test-secret-key"

        self.client = auth_app.app.test_client()

        auth_app.initialize_database()

    def tearDown(self):

        os.close(self.db_fd)
        os.unlink(self.db_path)

    # -----------------------------------------------------
    # TEST 1 - REGISTRATION
    # -----------------------------------------------------

    def test_registration(self):

        response = self.client.post(
            "/register",
            data={
                "username": "testuser",
                "password": "Test@123"
            },
            follow_redirects=True
        )

        self.assertIn(
            b"Account created successfully",
            response.data
        )

    # -----------------------------------------------------
    # TEST 2 - CORRECT LOGIN
    # -----------------------------------------------------

    def test_correct_login(self):

        self.client.post(
            "/register",
            data={
                "username": "testuser",
                "password": "Test@123"
            }
        )

        response = self.client.post(
            "/login",
            data={
                "username": "testuser",
                "password": "Test@123"
            },
            follow_redirects=True
        )

        self.assertIn(
            b"Authentication Successful",
            response.data
        )

    # -----------------------------------------------------
    # TEST 3 - INCORRECT PASSWORD
    # -----------------------------------------------------

    def test_incorrect_password(self):

        self.client.post(
            "/register",
            data={
                "username": "testuser",
                "password": "Test@123"
            }
        )

        response = self.client.post(
            "/login",
            data={
                "username": "testuser",
                "password": "wrongpassword"
            },
            follow_redirects=True
        )

        self.assertIn(
            b"2 attempt(s) remaining",
            response.data
        )

    # -----------------------------------------------------
    # TEST 4 - ACCOUNT LOCKOUT
    # -----------------------------------------------------

    def test_account_lockout(self):

        self.client.post(
            "/register",
            data={
                "username": "testuser",
                "password": "Test@123"
            }
        )

        for _ in range(3):

            response = self.client.post(
                "/login",
                data={
                    "username": "testuser",
                    "password": "wrongpassword"
                },
                follow_redirects=True
            )

        self.assertIn(
            b"Account locked after 3 incorrect login attempts",
            response.data
        )

    # -----------------------------------------------------
    # TEST 5 - CORRECT PASSWORD AFTER LOCKOUT
    # -----------------------------------------------------

    def test_correct_password_after_lockout(self):

        self.client.post(
            "/register",
            data={
                "username": "testuser",
                "password": "Test@123"
            }
        )

        for _ in range(3):

            self.client.post(
                "/login",
                data={
                    "username": "testuser",
                    "password": "wrongpassword"
                }
            )

        response = self.client.post(
            "/login",
            data={
                "username": "testuser",
                "password": "Test@123"
            },
            follow_redirects=True
        )

        self.assertIn(
            b"Account is locked",
            response.data
        )


if __name__ == "__main__":
    unittest.main()