from crypt import methods
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate(data, page):
    """paginate data into max formated items per page"""
    # get start and end index
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    # format data
    formated_data = [data_i.format() for data_i in data]
    return formated_data[start:end]

def format_categories(categories):
    return {category.id: category.type for category in categories}


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.all()
        except:
            abort(422)

        if not categories:
            abort(404)
    
        return jsonify({
            'success': True,
            'categories': format_categories(categories)
        })

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
    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            questions = Question.query.order_by(Question.id).all()
            categories = Category.query.order_by(Category.id).all()
            page = request.args.get('page', 1, type=int)
            formated_questions = paginate(questions, page)

            return jsonify({
                'success': True,
                'questions': formated_questions,
                'categories': format_categories(categories),
                'totalQuestions': len(questions),
                'currentCategory': None
            })

        except:
            abort(422)


    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)

            if question is None:
                abort(404)
            else:
                question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id
            })

        except:
            abort(422)
    

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        if not ('question' in body and 'answer' in body and 'category' in body and 'difficulty' in body):
            abort(400)

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty
            )
            question.insert()

            return jsonify({
                'success': True,
                'created': question.id
            })

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
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            body = request.get_json()
            search_term = body.get('searchTerm', None)

            if not search_term:
                abort(404)
                #questions = Question.query.order_by(Question.id).all()
            else:
                questions = Question.query.filter(Question.question.ilike(f"%{search_term}%")).all()
            page = request.args.get('page', 1, type=int)
            formated_questions = paginate(questions, page)

            return jsonify({
                'success': True,
                'questions': formated_questions,
                'totalQuestions': len(questions)
            })

        except:
            abort(404)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_question_by_category(category_id):
        try:
            ##
            categories = Category.query.order_by(Category.type).all()
            if category_id not in categories:
                abort(404)
            ##
            questions = Question.query.filter_by(category=str(category_id)).order_by(Question.id).all()
            page = request.args.get('page', 1, type=int)
            formated_questions = paginate(questions, page)

            return jsonify({
                'success': True,
                'questions': formated_questions,
                'totalQuestions': len(questions),
                'currentCategory': category_id
            })

        except:
            abort(422)

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
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            body = request.get_json()
            if not body:
                abort(400)
            if not ("previous_questions" in body and "quiz_category" in body):
                abort(400)
            previous_questions = body.get("previous_questions")
            quiz_category = body.get("quiz_category")
            categories = Category.query.all()
            #print(categories)

            if int(quiz_category['id']) > 0:
                next_question = Question.query \
                    .filter(Question.category == int(quiz_category['id'])) \
                    .filter(Question.id.notin_(previous_questions)) \
                    .all()
            else:
                next_question = Question.query \
                    .filter(Question.id.notin_(previous_questions)) \
                    .all()

            if next_question:
                # get random formated question
                formated_question = random.choice(next_question).format()

                return jsonify({
                    'success': True,
                    'question': formated_question
                })
            else:
                None #abort(404)

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
            "message": "Bad Request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404


    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    return app

