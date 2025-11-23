import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask, session
from app import create_app
from models import User, db
from controllers import api


class TestLogin:
    """Test cases for the Login resource class"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup method that runs before each test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create a test user
            self.test_user = User(username='testuser')
            self.test_user.set_password('testpassword')
            db.session.add(self.test_user)
            db.session.commit()
            
            # Store user ID for tests
            self.test_user_id = self.test_user.id

    def teardown_method(self):
        """Cleanup after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_successful_login(self):
        """Test successful login with valid credentials"""
        login_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        
        response = self.client.post('/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        # Check response
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["Message"] == "Login successful"
        
        # Check that session is set
        with self.client.session_transaction() as sess:
            assert "user_id" in sess
            assert sess["user_id"] == self.test_user_id

    def test_login_invalid_username(self):
        """Test login with non-existent username"""
        login_data = {
            "username": "nonexistentuser",
            "password": "testpassword"
        }
        
        response = self.client.post('/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        # Check response
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data["Message"] == "Invalid credentials"
        
        # Check that session is not set
        with self.client.session_transaction() as sess:
            assert "user_id" not in sess

    def test_login_invalid_password(self):
        """Test login with correct username but wrong password"""
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        
        response = self.client.post('/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        # Check response
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data["Message"] == "Invalid credentials"
        
        # Check that session is not set
        with self.client.session_transaction() as sess:
            assert "user_id" not in sess

    def test_login_empty_username(self):
        """Test login with empty username"""
        login_data = {
            "username": "",
            "password": "testpassword"
        }
        
        response = self.client.post('/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        # Check response
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data["Message"] == "Invalid credentials"
        
        # Check that session is not set
        with self.client.session_transaction() as sess:
            assert "user_id" not in sess

    def test_login_empty_password(self):
        """Test login with empty password"""
        login_data = {
            "username": "testuser",
            "password": ""
        }
        
        response = self.client.post('/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        # Check response
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data["Message"] == "Invalid credentials"
        
        # Check that session is not set
        with self.client.session_transaction() as sess:
            assert "user_id" not in sess

    def test_login_missing_username(self):
        """Test login with missing username field"""
        login_data = {
            "password": "testpassword"
        }
        
        response = self.client.post('/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        # Check response
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data["Message"] == "Invalid credentials"
        
        # Check that session is not set
        with self.client.session_transaction() as sess:
            assert "user_id" not in sess

    def test_login_missing_password(self):
        """Test login with missing password field"""
        login_data = {
            "username": "testuser"
        }
        
        response = self.client.post('/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        # Check response
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data["Message"] == "Invalid credentials"
        
        # Check that session is not set
        with self.client.session_transaction() as sess:
            assert "user_id" not in sess

    def test_login_empty_json(self):
        """Test login with empty JSON payload"""
        response = self.client.post('/login', 
                                  data=json.dumps({}),
                                  content_type='application/json')
        
        # Check response
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data["Message"] == "Invalid credentials"
        
        # Check that session is not set
        with self.client.session_transaction() as sess:
            assert "user_id" not in sess

    def test_login_no_json_content_type(self):
        """Test login without proper JSON content type"""
        login_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        
        response = self.client.post('/login', data=login_data)
        
        # Should still work as Flask can parse form data
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["Message"] == "Login successful"

    def test_login_case_sensitive_username(self):
        """Test that username is case sensitive"""
        login_data = {
            "username": "TestUser",  # Different case
            "password": "testpassword"
        }
        
        response = self.client.post('/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        # Check response
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data["Message"] == "Invalid credentials"
        
        # Check that session is not set
        with self.client.session_transaction() as sess:
            assert "user_id" not in sess

    def test_login_special_characters_in_username(self):
        """Test login with special characters in username"""
        # First create a user with special characters
        with self.app.app_context():
            special_user = User(username='user@domain.com')
            special_user.set_password('testpassword')
            db.session.add(special_user)
            db.session.commit()
            special_user_id = special_user.id

        login_data = {
            "username": "user@domain.com",
            "password": "testpassword"
        }
        
        response = self.client.post('/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        # Check response
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["Message"] == "Login successful"
        
        # Check that session is set
        with self.client.session_transaction() as sess:
            assert "user_id" in sess
            assert sess["user_id"] == special_user_id

    def test_login_long_password(self):
        """Test login with a very long password"""
        long_password = "a" * 1000  # 1000 character password
        
        # First create a user with long password
        with self.app.app_context():
            long_pass_user = User(username='longpassuser')
            long_pass_user.set_password(long_password)
            db.session.add(long_pass_user)
            db.session.commit()

        login_data = {
            "username": "longpassuser",
            "password": long_password
        }
        
        response = self.client.post('/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        # Check response
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["Message"] == "Login successful"

    @patch('controllers.User.query')
    def test_login_database_error(self, mock_query):
        """Test login when database query fails"""
        mock_query.filter_by.return_value.first.side_effect = Exception("Database error")
        
        login_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        
        response = self.client.post('/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        # Should handle the error gracefully
        assert response.status_code == 500

    def test_login_session_persistence(self):
        """Test that login session persists across requests"""
        login_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        
        # First login
        response = self.client.post('/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        
        # Make another request to verify session persists
        with self.client.session_transaction() as sess:
            assert "user_id" in sess
            assert sess["user_id"] == self.test_user_id

    def test_login_with_none_username(self):
        """Test login with None username"""
        login_data = {
            "username": None,
            "password": "testpassword"
        }
        
        response = self.client.post('/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        # Check response
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data["Message"] == "Invalid credentials"

    def test_login_with_none_password(self):
        """Test login with None password"""
        login_data = {
            "username": "testuser",
            "password": None
        }
        
        response = self.client.post('/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        # Check response
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data["Message"] == "Invalid credentials"


if __name__ == '__main__':
    pytest.main([__file__])

