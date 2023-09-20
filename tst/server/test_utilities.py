import unittest
from unittest.mock import patch

from src.server import app
from src.server.utilities import DBAgent


class TestDBAgentMethods(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

    @patch('sqlite3.connect')
    def test_load_user(self, mock_connect):
        mock_cursor = mock_connect().cursor()
        mock_cursor.fetchone.return_value = [1, 'username', 'password', 'email', 'admin']
        result = app.load_user(1)
        self.assertEqual(result.id, 1)
        self.assertEqual(result.username, 'username')
        self.assertEqual(result.password, 'password')
        self.assertEqual(result.role, 'admin')

    @patch('app.DBAgent.execute_query')
    def test_register(self, mock_execute):
        mock_execute.return_value = None  # Assume the DB query executes without issue
        response = self.app.post('/register', data=dict(username='test', password='password'), follow_redirects=True)
        self.assertTrue(b'Registration successful! Please login.' in response.data)

    @patch('app.DBAgent.execute_query')
    def test_add_skill(self, mock_execute):
        mock_execute.return_value = None  # Assume the DB query executes without issue
        with self.app as c:
            with c.session_transaction() as sess:
                sess['logged_in'] = True  # Mocking a logged-in session
            response = self.app.post('/admin/add_skill',
                                     data=dict(name='skill_name', description='description', price='19.99',
                                               launch_date='2023-01-01', category_id=1), follow_redirects=True)
        self.assertTrue(b'Skill created successfully' in response.data)

    @patch('app.DBAgent.execute_query')
    def test_db_agent_execute_query(self, mock_execute):
        db_agent = DBAgent()
        db_agent.execute_query("INSERT INTO Users (Username, Email, Password, Role) VALUES (?, ?, ?, 'admin')",
                               ('username', 'email', 'password'))
        mock_execute.assert_called_with("INSERT INTO Users (Username, Email, Password, Role) VALUES (?, ?, ?, 'admin')",
                                        ('username', 'email', 'password'))
