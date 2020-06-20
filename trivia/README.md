# Full Stack API Final Project

## Endpoints

### /categories

this endpoint returns all the categories for the various quizzes.  the response looks like this:

```
{'success': True, 
	'categories': {{'id': 1, 'type': 'Science'}, {'id': 2, 'type': 'Art'}}
}
```

###  /questions

this endpoint takes a url argument /questions?page=1 and returns all categories for the given page.  the response looks like this:

```
{
	'success': True,
	'questions': [
		{'id': 1,
			'question': 'Whose autobiography is entitled 'I know Why the Caged Bird Sings'?',
			'answer': 'Maya Angelous',
			'category': 2,
			'difficulty': 2}
	]
	'total_questions': 1,
	'categories': {{'id': 1, 'type': 'Science'}, {'id': 2, 'type': 'Art'}},
	'current_category': ''
}
```

### /questions/1

this endpoint deletes a given question by using the question id in the route.  The response is:

```
{'success': True}
```

### /questions

this endpoint posts a new question OR returns search results.  If it does not find 'searchTerm' in the object it receives it takes in this data and adds it to the database:

```
{
	'question': 'Who wrote Watchmen?',
	'answer': 'Alan Moore',
	'difficulty': 3,
	'category': 2
}
```

and returns:

```
{
	'success': True
}

if the endpoint receives:

```
{
	'searchTerm': 'Caged Bird'
}
```

it returns:

```
'success': True,
'questions': [
	{
		'id': 1,
		'question': 'Whose autobiography is entitled 'I know Why the Caged Bird Sings'?',
		'answer': 'Maya Angelous',
		'category': 2,
		'difficulty': 2
	}
	]
'totalQuestions': 1
'currentCategory': ''
```

### /categories/1/questions

this enpoint takes in the category id in the endpoint and returns the questions for the given category.  The response looks like this:

```
{'success': True,
'questions': [
	{
		'id': 1,
		'question': 'Whose autobiography is entitled 'I know Why the Caged Bird Sings'?',
		'answer': 'Maya Angelous',
		'category': 2,
		'difficulty': 2
	}
]
'total_questions': 1,
'current_category': 2}
```

### /quizzes

this endpoint takes in a json object that has the ids of the previous questions the user has answered and the category of questions they have chosen.  It looks like this:

```
{
	'previous_questions': [],
	'quiz_category': 2
}
```

it returns a random question that it's id does not match one of the numbers in the previous_questions list.  The returned object looks like this:

```
{
	'success': True,
	'question': {
		'id': 1,
		'question': 'Whose autobiography is entitled 'I know Why the Caged Bird Sings'?',
		'answer': 'Maya Angelous',
		'category': 2,
		'difficulty': 2
	}
}
```