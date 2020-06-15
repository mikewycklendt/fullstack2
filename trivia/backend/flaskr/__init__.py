import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

#def create_app(test_config=None):
  # create and configure the app
app = Flask(__name__)
setup_db(app)
  
'''
@TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
'''
CORS(app, resources={r"/*": {"origins": "*"}})
'''
@TODO: Use the after_request decorator to set Access-Control-Allow
'''
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response
'''
@TODO: 
Create an endpoint to handle GET requests 
for all available categories.
'''
@app.route('/categories', methods=['GET'])
def get_categories():

  categories = Category.query.order_by(Category.type).all()
  #categories_formatted = {category.format() for category in categories}

  return jsonify({
    'success': True,
    'categories': {category.id: category.type for category in categories}
  })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
@app.route('/questions', methods=['GET'])
def get_questions():

  questions = Question.query.all()

  categories = Category.query.all()

  formatted_categories = [category.format() for category in categories]

  print(formatted_categories)

  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  formatted_questions = [question.format() for question in  questions]
  current_questions = formatted_questions[start:end]

  print(current_questions)

  return jsonify({
    'success': True,
    'questions': current_questions,
    'total_questions': len(formatted_questions),
    'categories': {category.id: category.type for category in categories},
    'current_category': ''
  })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
@app.route('/categories/<int:category_id>/questions')
def questions_by_category(category_id):

  questions = Question.query.filter(Question.category == str(category_id)).all()

  formatted_questions = [question.format() for question in questions]
  total_questions = len(formatted_questions)

  return jsonify({
    'success': True,
    'questions': formatted_questions,
    'total_questions': total_questions,
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

@app.route('/quizzes', methods=['POST'])
def quizzes():

  body = request.get_json()
  previous_questions = body['previous_questions', None]
  quiz_category = body.get['quiz_category', None]

  questions = Question.query.filter(Question.category == quiz_category)\
    
  formatted_questions = [question.format() for question in questions]
  filtered_questions = []

  for question in formatted_questions:
    for previous_question in previous_questions:
      if previous_question == question.id:
        print('question ' + question.id + ' filtered')
      else:
        filtered_questions += question
          
  returned_question = random.choice(filtered_questions)

  return jsonify({
    'success': True,
    'question': returned_question.id
  })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  
if __name__ == '__main__':
  app.debug = True
  app.run(host='0.0.0.0', port=81)

    