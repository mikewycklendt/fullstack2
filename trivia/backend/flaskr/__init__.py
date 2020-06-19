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

@app.route('/categories', methods=['GET'])
def get_categories():
  try:
    categories = Category.query.order_by(Category.type).all()

    return jsonify({
      'success': True,
      'categories': {category.id: category.type for category in categories}
    })
  except:
    abort(404)

@app.route('/questions', methods=['GET'])
def get_questions():
  try:
    questions = Question.query.all()
    categories = Category.query.all()

    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    formatted_questions = [question.format() for question in  questions]
    current_questions = formatted_questions[start:end]

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(formatted_questions),
      'categories': {category.id: category.type for category in categories},
      'current_category': ''
    })
  except:
    abort(404)

@app.route('/questions/<int:id>', methods=['DELETE'])
def delete_question(id):
  try:
    question = Question.query.filter(Question.id==id).one_or_none()
    question.delete()
    return jsonify({'success': True})
  except:
    abort(422)

@app.route('/questions', methods=['POST'])
def add_question():
  body = request.get_json()
  print(body)
  question = body.get('question', None)
  answer = body.get('answer', None)
  difficulty = body.get('difficulty', None)
  category = body.get('category', None)
  search = body.get('searchTerm', None)

  try:
    if search:
      results = Question.query.order_by(Question.question).filter(Question.question.ilike('%{}%'.format(search)))
      questions = [result.format() for result in results]
      totalQuestions = len(questions)

      return jsonify({
        'success': True,
        'questions': questions,
        'totalQuestions': totalQuestions,
        'currentCategory': ''
      })
    else:
      addQuestion = Question(question=question, answer=answer, difficulty=difficulty, category=category)
      addQuestion.insert()
      return jsonify({'success': True})

  except:
    abort(422)

@app.route('/categories/<int:category_id>/questions')
def questions_by_category(category_id):
  try:
    questions = Question.query.filter(Question.category == str(category_id)).all()

    formatted_questions = [question.format() for question in questions]
    total_questions = len(formatted_questions)

    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': total_questions,
      'current_category': category_id
    })
  except:
    abort(404)

@app.route('/quizzes', methods=['POST'])
def quizzes():
  #try:
  body = request.get_json()
  previous_questions = body['previous_questions']
  quiz_category = body['quiz_category']

  if quiz_category['id'] == 0:
    questions = Question.query.all()
  else:
    questions = Question.query.filter(Question.category == quiz_category['id'])
    
  formatted_questions = [question.format() for question in questions]

  if previous_questions != []:
    for question in formatted_questions:
      for previous_question in previous_questions:
        if previous_question == question['id']:
          print('question ' + str(previous_question) + ' removed')
          formatted_questions.remove(question)

  print(previous_questions)
  print(formatted_questions)

  return jsonify({
    'success': True,
    'question': returned_question
  })
  #except:
  #  abort(400)
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
@app.errorhandler(404)
def not_found(error):
  return jsonify({
    'success': False,
    'error': 404,
    'message': 'resource not found'
  }), 404
  
@app.errorhandler(400)
def bad_request(error):
  return jsonify({
    'success': False,
    'error': 400,
    'message': 'bad request'
  }), 400

@app.errorhandler(422)
def unprocessable(error):
  return jsonify({
    'success': False,
    'error': 422,
    'message': 'unprocessable'
  }), 422

if __name__ == '__main__':
  app.debug = True
  app.run(host='0.0.0.0', port=81)

    