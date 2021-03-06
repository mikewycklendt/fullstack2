#!/usr/bin/python3

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
import sys
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@3.134.26.61:5432/todoapp'
db = SQLAlchemy(app)
#db = SQLAlchemy(app, session_options={"expire_on_commit": False})

migrate = Migrate(app, db)

class Todo(db.Model):
	__tablename__ = 'todos'
	id = db.Column(db.Integer, primary_key=True)
	description = db.Column(db.String(), nullable=False)
	completed = db.Column(db.Boolean, nullable=False, default=False)
	list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

class TodoList(db.Model):
	__tablename__ = 'todolists'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(), nullable=False)
	todos = db.relationship('Todo', backref='list', lazy=True)

#order_items = db.Table('order_items',
#    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
#    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
#)

#class Order(db.Model):
#  id = db.Column(db.Integer, primary_key=True)
#  status = db.Column(db.String(), nullable=False)
#  products = db.relationship('Product', secondary=order_items,
#      backref=db.backref('orders', lazy=True))
#
#class Product(db.Model):
#  id = db.Column(db.Integer, primary_key=True)
#  name = db.Column(db.String(), nullable=False)

# flask db migrate
# flask db upgrade

#	def __repr__(self):
#		return f'<Todo {self.id} {self.description}>'	

#db.create_all()

#todo1 = Todo(description='Todo Thing 1')
#db.session.add(todo1)
#db.session.commit()

# list = TodoList(name='Urgent')
# todo = Todo(description="This really important Thing")
# todo2 = Todo(description="Urgent Todo 2")
# todo3 = Todo(description="Urgent Todo 3")
# todo.list = list
# todo2.list = list
# todo3.list = list
# db.session.add(list)
# db.session.commit()

@app.route('/lists/<list_id>')
def get_list_todos(list_id):
	return render_template('index.html', active_list=TodoList.query.get(list_id), todos=Todo.query.filter_by(list_id=list_id).order_by('id').all(), lists=TodoList.query.all())

@app.route('/')
def index():
	return redirect(url_for('get_list_todos', list_id=1))

@app.route('/todos/create', methods=['POST'])
def create_todo():
	error = False
	body = {}
#	description = request.form.get('description', '')
#	return render_template('index.html')
	try:
		description = request.get_json()['description']
		todo = Todo(description=description)
		#body['description'] = todo.description
		db.session.add(todo)
		db.session.commit()
		body['id'] = todo.id
		body['completed'] = todo.completed
		body['description'] = todo.description
	except:
		error=True
		db.session.rollback()
		print(sys.exc_info())
	finally:
		db.session.close()
	if error:
		abort (400)
	else:
		return jsonify(body)
#		return jsonify({
#			'description': todo.description
#		})

#	return redirect(url_for('index'))

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
	try:
		completed = request.get_json()['completed']
		print('completed', completed)
		todo = Todo.query.get(todo_id)
		todo.completed = completed
		db.session.commit()
	except:
		db.session.rollback()
	finally:
		db.session.close
	return redirect(url_for('index'))

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
	try:
		Todo.query.filter_by(id=todo_id).delete()
		db.session.commit()
	except:
		db.session.rollback()
	finally:
		db.session.close()
	return jsonify({'success': True })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)