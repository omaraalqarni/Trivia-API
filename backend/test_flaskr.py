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
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
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
    Write at least one test for each test
    for successful operation and for expected errors.
    """
    # testing both pagination and get_questions and their error

    def test_question_pagination(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_404_get_questions_pagination(self):
        # testing get request for questions
        res = self.client().get('/questions?page=20520')
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Page not found')

    # testing get categories and its error if not found (404)
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_404_get_categories(self):
        res = self.client().get('/categories/3832')
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Page not found')

    # testing the deletion of questions
    def test_delete_question(self):
        # Creating dummy question with its answer,difficulty, and category.
        test_question = Question(
            question='what is the capital of Saudi Arabia',
            answer='Riyadh',
            difficulty=2,
            category=3)
        # insert the question
        test_question.insert()
        test_question_id = test_question.id

        res = self.client().delete(f'/questions/{test_question_id}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'question deleted')

    def test_422_questionDoesNotExist(self):
        res = self.client().delete('/questions/555')
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'page is unprocessable')

    # test add question & test 422

    def test_add_question_success(self):
        test_question = {
            'question': 'What does FSND mean',
            'answer': 'Full Stack Nanodegree',
            'difficulty': 1,
            'category': 1
        }
        res = self.client().post('/questions', json=test_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'question added')
       
    def add_empty_question(self):
        test_question = {
            'question':'',
            'answer':'',
            'difficulty':'',
            'category':''
        }
        res = self.client().post('/questions', json=test_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'page is unprocessable')

    # test search_questions
    def test_search_questions(self):
        request_data = {
            'searchTerm': 'author Anne Rice',
        }
        res = self.client().post('/questions/search', json=request_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        # the result has to be 1
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_404_search_question(self):
        res = self.client().post('/question', json={'searchTerm': 'FSND'})
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Page not found')

    def test_get_questions_by_category(self):
        # getting questions by category 5 which is Entertainment
        res = self.client().get('/categories/5/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 5)

    def test_404_get_questions_by_categories(self):
        # request a category that does not exist yet
        res = self.client().get('/categories/15/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Page not found')

    # Testing start_quiz:

    def test_start_quiz(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [20, 21],
            'quiz_category': {'type': 'Science', 'id': '1'}})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_400_start_quiz(self):
        res = self.client().post('/quizzes', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
