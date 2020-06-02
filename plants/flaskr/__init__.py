from flask import Flask, jsonify, request
from models import setup_db, Plant
from flask_cors import CORS

def create_app(test_config=None):
	#app = Flask(__name__)
	app = Flask(__name__, instance_relative_config=True)
	setup_db(app)
	CORS(app)
	#CORS(app, resources{r'*/api/*': {origins: '*'}})

	@app.after_request
	def after_request(response):
		response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
		response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
		return response

	@app.route('/plants')
	def get_plants():
		page = request.args.get('page', 1, type=int)
		start = (page - 1) * 10
		end = start + 10
		plants = Plant.query.all()
		formatted_plants = [plant.format() for plant in plants]
		return jsonify({'success':True, 
						'plants': formatted_plants[start:end],
						'total_plants': len(formatted_plants)
						})


	#app = Flask(__name__, instance_relative_config=True)
	#app.config.from_mapping(
	#	SECRET_KEY='DEV',
	#	DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
	#)

	#if test_config is None:
	# load the instance config, if it exists, when not testing
	#	app.config.from_pyfile('config.py', silent=True)
	#else:
		# load the test config if passed in
	#	app.config.from_mapping(test_config)


	return app

# export FLASK_APP=flaskr
# export FLASK_ENV=development
# flask run

# sudo pip3 install flask-cors

#app.config.from_mapping(
#	SECRET_KEY='dev',
#	DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
#	)



#try:
#	os.makedirs(app.instance_path)
#except OSError:
#	pass

#curl
	#-X or --request COMMAND
	#-d or --data DATA
	#-F or --form CONTENT
	#-u or --user USER[:PASSWORD]
	#-H or --header LINE