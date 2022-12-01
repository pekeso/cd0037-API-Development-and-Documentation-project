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
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)

        self.new_question = {
            "question": "What's the most populous country in the world?",
            "answer": "China",
            "category": 4,
            "difficulty": 2
        }

        self.bad_new_question = {
            "question": "What's the most populous country in the Africa?",
            "answer": "",
            "category": 0,
            "difficulty": 2
        }

        self.random_quiz = {
            "quiz_category": {
                "type": "Art", 
                "id": "2"
            },
            "previous_questions": []
        }

        self.bad_random_quiz = {
            "quiz_category": {
                "type": "Art", 
                "id": "8"
            },
            "previous_questions": []
        }

        # binds the app to the current context
        with self.app.app_context():
            setup_db(self.app, self.database_path)
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
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))

    """
    Test for successful retrieve of questions
    """
    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])
        self.assertTrue(data["categories"])

    """
    Test for failed retrieve of questions
    """
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    """
    Test for resource deletion
    """
    def test_delete_question(self):
        res = self.client().delete('/questions/4')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 4)

    """
    Test for deletion of non existing resource
    """
    def test_404_if_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
    
    """
    Test question search with results
    """
    def test_get_question_search_with_results(self):
        res = self.client().post("/questions/search", json={"searchTerm": "autobiography"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["totalQuestions"])
        self.assertEqual(len(data["questions"]), 1)

    """
    Test question search without results
    """
    def test_get_question_search_without_results(self):
        res = self.client().post("/questions/search", json={"searchTerm": "joel"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["totalQuestions"], 0)
        self.assertEqual(len(data["questions"]), 0)

    """
    Test for successful retrieval of questions by category
    """
    def test_get_question_by_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])

    """
    Test for unsuccessful retrieval of questions by category
    """
    def test_404_if_category_does_not_exist(self):
        res = self.client().get("/categories/10/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    """
    Test random question
    """
    def test_random_question(self):
        res = self.client().post("/quizzes", json=self.random_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    """
    Test failing random question
    """
    def test_random_question_fail(self):
        res = self.client().post("/quizzes", json=self.bad_random_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


    """
    Test to add new question
    """
    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        pass

    """
    Test failing to add new question
    """
    def test_422_if_question_creation_fails(self):
        res = self.client().post("/questions", json=self.bad_new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()