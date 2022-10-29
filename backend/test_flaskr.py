import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = f"postgresql://{'postgres'}:{'ocb'}@{'localhost:5432'}/{self.database_name}"
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories_happy_path(self):
        """test if we get the right respose from endpoint /category"""
        
        # get response
        response = self.client().get("/categories")
        data = json.loads(response.data)

        # check status code
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check body
        self.assertEqual(len(data["categories"]), len(Category.query.all()))


    def test_get_questions_happy_path(self):
        """test if we get the right respose from endpoint /questions"""
        
        response = self.client().get("/questions")
        data = json.loads(response.data)

        # check status code
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check body
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions'])<=data['total_questions'])
        self.assertTrue(len(data['questions'])<=10)
        self.assertEqual(len(data["questions"]), len(Category.query.all()))

######

    def test_create_question_happy_path(self):
        """test if we get the right respose when creating an 
        valid question at endpoint /questions"""

        question = {
            'question': 'How is performance of a CPU measured?',
            'answer': 'instructions per second',
            'difficulty': 3,
            'category': 5
        }
        
        response = self.client().post("/questions", json=question)
        data = json.loads(response.data)

        # check status code
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check body
        self.assertTrue(data['created'])
        self.question_id = data['created']


    def test_create_question_missing_question(self):
        """test if we get the right respose when creating an 
        invalid question at endpoint /questions"""

        question = {
            'answer': 'instructions per second',
            'difficulty': 3,
            'category': 5
        }
        
        response = self.client().post("/questions", json=question)
        data = json.loads(response.data)

        # check status code
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

######
    
    def test_delete_question_happy_path(self):
        """test if we get the right respose when deleting an existing 
        question at endpoint /questions/<int:question_id>"""

        #question_id = 9

        response = self.client().delete(f"/questions/{self.question_id}")
        data = json.loads(response.data)

        # check status code
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertEqual(data['deleted'], self.question_id)


    def test_delete_question_missing_question(self):
        """test if we get the right respose when deleting an non existing 
        question at endpoint /questions/<int:question_id>"""
        
        response = self.client().delete("/questions/999")
        data = json.loads(response.data)

        # check status code
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        
        # check body
        self.assertEqual(data['message'], 'Not Found')



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()