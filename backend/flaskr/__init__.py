import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

'''
@TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs.
'''
def create_app(test_config=None):
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resources={'/': {'origins': '*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
 
  @app.after_request
  def after_request(response):
     
      response.headers.add('Access-Control-Allow-Headers',
                            'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods',
                            'GET,PUT,POST,DELETE,OPTIONS')
      return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route("/categories")
  def get_categories():
    categories = Category.query.order_by(Category.type).all()
    if len(categories) < 1:
      abort(404)
    return jsonify({
      'success': True,
      'categories': {category.id: category.type for category in categories}
    })
    

  
  @app.route("/questions")
  def get_questions():
    selected = Question.query.order_by(Question.id).all()
    currentQuestions = paginate_questions(request, selected)
    categories = Category.query.order_by(Category.type).all()

    if len(currentQuestions) < 1:
      abort(404)
    return jsonify({
      'success':True,
      'questions':currentQuestions,
      'total_questions': len(selected),
      'categories': {category.id: category.type for category in categories},
      'current_category': None
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 
  '''
  @app.route('/questions/<question_id>', methods=['DELETE'])
  def delete_questions(question_id):
    try:
      question = Question.query.get(question_id)
      question.delete()
      return jsonify(({
        'success': True,
        'deleted': question_id
      }))
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  '''
  @app.route('/questions', methods=['POST'])
  def post_question():
    body = request.get_json()

    if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
        abort(422)
    
    new_question = body.get('question')
    new_answer = body.get('answer')
    new_difficulty = body.get('difficulty')
    new_category = body.get('category')
    
    try:
      question = Question(
        question=new_question,
        answer=new_answer,
        difficulty=new_difficulty,
        category =new_category)
      
      question.insert()

      return jsonify({
        'success': True,
        'message':'Question is added!'
      })
    except:
      abort(422)
    

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    search_term = body.get('searchTerm',None)
    if search_term:
      search_results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      return jsonify({
          'success': True,
          'questions': [question.format() for question in search_results],
          'total_questions': len(search_results),
          'current_category': None
      })
    abort(404)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_question_by_category(category_id):
    try:
      questions = Question.query.filter(Question.category==str(category_id)).all()
      
      return jsonify({
        'success': True,
        'questions':[question.format() for question in questions],
        'total_questions': len(questions),
        'current_category': category_id
      })
    except:
      abort(404)


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def start_quiz():
    try:
        body = request.get_json()
        if not ('quiz_category' in body and 'previous_questions' in body):
            abort(422)

        category = body.get('quiz_category')
        previous_questions = body.get('previous_questions')

        if category['type'] == 'click':
            available_questions = Question.query.filter(
                Question.id.notin_((previous_questions))).all()
        else:
            available_questions = Question.query.filter_by(
                category=category['id']).filter(Question.id.notin_((previous_questions))).all()

        new_question = available_questions[random.randrange(
            0, len(available_questions))].format() if len(available_questions) > 0 else None

        return jsonify({
            'success': True,
            'question': new_question
        })
    except:
        abort(422)



  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "bad request"
      }), 400

  return app     