import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(selected):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  questions = [question.format() for question in selected]
  currentQuestions = questions[start:end]
  return currentQuestions



  # '''
  # @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs.
  # '''
def create_app(test_config=None):
  app = Flask(__name__)
  setup_db(app)
  cors = CORS(app, resources={'/': {'origins': '*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request()
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,True')
    response.headers.add('Access-Control-Allow-Methods','GET,POST,DELETE')
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
    

#  '''
#  @TODO: 
#  Create an endpoint to handle GET requests for questions, 
#  including pagination (every 10 questions). 
#  This endpoint should return a list of questions, 
#  number of total questions, current category, categories. 
#  '''
  
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
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 
  '''
  @app.route('/questions/<int: question_id>', methods=["DELETE"])
  def delete_questions(question_id):
    try:
      question = Question.query.get(question_id)
      question.delete()
      return jsonify({
        'success': True,
        'deleted': question_id
      })
    except:
      abort(422)

  '''
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  '''
  @app.route('/questions', methods=['POST'])
  def post_question():
    body = request.get_json()
    question = body.get('question','')
    answer = body.get('answer','')
    difficulty = body.get('difficulty','')
    category = body.get('category','')

    if (question or answer or difficulty or category) == '':
      abort(422)
    
    try:
      new_question = Question(
        question=question,
        answer=answer,
        difficulty=difficulty,
        category =category)
      question.insert()

      return jsonify({
        'success': True,
        'created':question.id,
        'message':'Question is added!'
      })
    except:
      abort(422)
    
  '''
  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    searchTerm = body.get('searchTerm','')
    if searchTerm == '':
      abort(422)

    search_results = Question.query.filter(Question.question.ilike(f'%{searchTerm}%')).all()
    return jsonify({
                'success': True,
                'questions': [question.format() for question in search_results],
                'total_questions': len(search_results),
                'current_category': None
            })

  '''
  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 
  '''
  @app.route('/categories/<int:category_id/questions>', methods=['GET'])
  def get_question_by_category(category_id):
    try:
      questions = Question.query.filter(Question.category==str(category_id)).all()
      
      return jsonify({
        'success': True,
        'question':[question.format() for question in questions],
        'number_of_questions': len(questions),
        'current_category': category_id
      })
    except:
      abort(404)

    
  '''
  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def start_quiz():
    body = request.get_json
    category = body.get('category')
    previous_questions = body.get('previous_questions')
    if (category is None) or ( previous_questions is None):
      abort(400)

    if (category['id'] == 0):
          questions = Question.query.all()
    else:
      questions = Question.query.filter_by(category=category['id']).all()

    def get_random_question():
        return questions[random.randint(0, len(questions)-1)]
    next_question = get_random_question()

    exists = True
    while exists:
      if next_question.id in previous_questions:
          next_question = get_random_question()
      else:
          exists = False

    return jsonify({
          'success': True,
          'question': next_question.format(),
      }), 200
      
  '''
  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  return app

      