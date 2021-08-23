import os
from unittest.signals import removeResult
from warnings import catch_warnings
from flask import Flask, request, abort, jsonify
from flask.globals import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def pagination(request,selected):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selected]
  current_page = questions[start:end]
  return current_page



def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app,resources={"r/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods','GET,POST,DELETE')
      return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.order_by(Category.id).all()
    if len(categories) == 0:
      abort(404)
    return jsonify({
      'success': True,
      #to retrieve every category separately
      'categories': {category.id: category.type for category in categories}
    })
    
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  '''
  @app.route('/questions')
  def get_questions():
    selected = Question.query.order_by(Question.id).all()
    current_question_page = pagination(request,selected)
    #query categories to add the info to questions
    categories = Category.query.order_by(Category.type).all()
    if len(current_question_page) == 0:
      abort(404)
    return jsonify({
      'success': True,
      'questions': current_question_page,
      'total_question' : len(selected),
      'categories': {category.id: category.type for category in categories}
    })
     


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<question_id>',methods=['DELETE'])
  def delete_question(question_id):
    try:
       question = Question.query.get(question_id)
       return jsonify({
         'success': True,
         'message': 'question deleted'
       })
    except:
        abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  TEST: When yo u submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions',methods=['POST'])
  def add_question():
    question = request.json.get('question')
    answer = request.json.get('answer')
    difficulty= request.json.get('difficulty')
    category = request.json.get('category')
    if not(question and answer and difficulty and category):
      abort(400)
    new_question = Question(question,answer,category,difficulty)
    new_question.insert()
    return jsonify({
      'success':True,
      'message': 'question added'
    })
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 
  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', method=['POST'])
  def search_questions():
    data = request.get_json()
    searchTerm = data.get('searchTerm')
    search_results = Question.query.filter(Question.question.ilike(f"%{searchTerm}%")).all()
    questions = pagination(request,search_results)
    total_of_questions = len(questions)
    if total_of_questions == 0:
      abort(404)
    return jsonify({
      'success':True,
      'total_questions': total_of_questions,
      'questions':questions,
      'current_category': None 
    })
    

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 
  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id/questions', methods=['GET'])
  def get_questions_by_categories(category_id):
    selected = Question.query.filter_by(category=category_id).all()
    questions = pagination(request,selected)
    total_of_questions = len(questions)
    if total_of_questions == 0:
      abort(404)
    return jsonify({
      'success':True,
      'questions':questions,
      'total_questions': total_of_questions,
      'current_category': category_id
     })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 
  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes',methods=['POST'])
  def start_quiz():
    data = request.get_json()
    previous_questions = data.get("previous_questions")
    quiz_category = data.get("quiz_category")
    quiz_category_id = int(quiz_category["id"])

    question = Question.query.filter(
        Question.id.notin_(previous_questions)
    )

    # quiz category id is 0 if all is selected and therefore false
    if quiz_category_id:
        question = question.filter_by(category=quiz_category_id)

    # limit result to only one question
    question = question.first().format()

    return jsonify({"success": True, "question": question, }), 200
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error_code': 400,
      'message': 'Bad request'
    })
  
  @app.errorhandler(404)
  def page_not_found(error):
    return jsonify({
      'success': False,
      'error_code': 404,
      'message':'Page not found'
    })

  @app.errorhandler(422)
  def unprocessable(error):
    return({
      'success': False,
      'error_code': 422,
      'message': 'page is unprocessable'
    })


  
  return app

    