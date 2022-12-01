import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    with app.app_context():
        setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def retrieve_categories():
        categories = Category.query.order_by(Category.id).all()
        categories = [category.format() for category in categories]

        categories_dict = {}
        for i in range(len(categories)):
                categories_dict[categories[i]["id"]] = categories[i]["type"]

        if len(categories) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": categories_dict
            }
        )

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions")
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        categories = Category.query.order_by(Category.id).all()

        for category in categories:
            current_category = category.type

        categories_dict = {category.id: category.type for category in categories}
        
        # print(current_category)

        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
                "current_category": current_category,
                "categories": categories_dict
            }
        )

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                }
            )

        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)

        try:
            if (not new_question) or (not new_answer) or (not new_category) or (not new_difficulty):
                abort(400)
            question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
            question.insert()

            # print(question.format())
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True
                }
            )

        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions/search", methods=["POST"])
    def search_question():
        body = request.get_json()

        search = body.get("searchTerm", None)

        try:
            selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search))
                )
                
            current_questions = paginate_questions(request, selection)
            # print(current_questions)
            categories = Category.query.order_by(Category.id).all()
            categories = [category.format() for category in categories]

            categories_dict = {}
            for i in range(len(categories)):
                    categories_dict[categories[i]["id"]] = categories[i]["type"]

            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "totalQuestions": len(selection.all())
                }
            )
        except:
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<id>/questions")
    def get_question_by_category(id):
        category = Category.query.filter(Category.id == id).one_or_none()

        if category is None:
            abort(404)

        category = category.format()
        selection = Question.query.order_by(Question.id).filter(Question.category == category["id"])
        current_questions = paginate_questions(request, selection)

        # print(category["id"])

        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(current_questions),
                "current_category": category["type"]
            }
        )

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def get_random_question():
        try:
            body = request.get_json()

            quiz_category = body.get("quiz_category")
            previous_questions = body.get("previous_questions")

            # print(quiz_category["type"])

            if quiz_category is None:
                abort(404)

            categories = Category.query.order_by(Category.id).all()
            categories_dict = {category.id: category.type for category in categories}

            category_id = quiz_category["id"]

            if category_id == 0:
                category_id = random.randint(1, 6)

            # Get all questions from the selected category
            selection = Question.query.order_by(Question.id).filter(Question.category == category_id)
            current_questions = paginate_questions(request, selection)

            if len(current_questions) == 0:
                abort(404)

            # Get the question IDs from the selected category
            question_ids = []
            for i in range(len(current_questions)):
                question_ids.append((current_questions[i]["id"]))

            # Get the differences between the selected category question IDs and the request
            # body previous questions
            differences = []
            for elem in question_ids:
                if elem not in previous_questions:
                    differences.append(elem)

            # If the differences list is empty return all categories
            if len(differences) == 0:
                return jsonify (
                    {
                        "success": True,
                        "categories": categories_dict
                    }
                )

            # Get a random question from the selected category
            question_id = random.choice(differences)
            question = {}
            for i in range(len(current_questions)):
                if question_id == current_questions[i]["id"]:
                    question = current_questions[i]

            return jsonify(
                {
                    "success": True,
                    "question": question
                }
            )
        except:
            abort(422)


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
                "success": False, 
                "error": 400, 
                "message": "bad request"
            }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
                "success": False, 
                "error": 404, 
                "message": "resource not found"
            }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
                "success": False, 
                "error": 405, 
                "message": "method not allowed"
            }), 405
        
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
                "success": False, 
                "error": 422, 
                "message": "unprocessable"
            }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
                "success": False, 
                "error": 500, 
                "message": "server could not respond due to an internal server error"
            }), 500

    return app

