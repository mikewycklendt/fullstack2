# Import all dependencies
import os
import unittest
import json
from flaskr import create_app
from models import setup_db, Book

class BookshelfTestCase(unittest.TestCase):
    """This class represents the resource test case"""

    def setUp(self):
        """ Executed before each test.  
			Setup Database
			Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "bookshelf_test"
        self.database_path = "postgres+psycopg2://postgres:postgres@{}/{}".format('3.134.26.61:5432', self.database_name)
        setup_db(self.app, self.database_path)

		self.new_book = {
			'title': 'Game of Thrones',
			'author': 'George RR Martin',
			'rating': 5
		}

    def tearDown(self):
        """ Executed after each test
			When things are undone"""
        pass

	def test_get_paginated_books(self):
		res = self.client().get('/books')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertEqual(data['total_books'])
		self.assertEqual(data['books'])

	def test_404_sent_requesting_beyond_valid_page(self):
		res = self.client().get('/books?page=1000', json{'rating': 1})
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 404)
		self.assertEqual(data['success'], False)
		self.assertEqual(data['message'], 'resource not found')

	def test_update_book_rating(self):
		res = self.client().patch('/books/5', json={'rating': 1})
		data = json.loads(res.data)
		book = Book.query.filter(Book.id == 5).one_or_none()

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertEqual(book.format()['rating'], 1)

	def test_app_for_failed_update(self):
		res = self.client().patch('/books/5')
		data = json.loads(rEs.data)

		self.assertEqual(res.status_code, 400)
		self.assertEqual(data['success'], False)
		self.assertEqual(data['message'], 'bad request')

	def test_delete_book(self):
		res = self.client().delete('/books/1')
		data = json.loads(res.data)

		book = Book.query.filter(Book.id == 1).one_or_none()

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertEqual(data['deleted'], 1)
		self.assertEqual(data['total_books'])
		self.assertEqual(len(data['books']))
		self.assertEqual(book, None)

	def test_create_new_book(self):
		res = self.client().post('/books', json=self.new_book)
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success', True])
		self.assertEqual(data['created'])
		self.assertTrue(len(data['books']))

	def test_405_if_book_creation_not_allowed(self):
		res = self.client().post('/books/45', json=self.new_book)
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 405)
		self.assertEqual(data['success'], True)
		self.assertEqual(data['message'], 'method not allowed')

	def test_get_book_search_with_results(self):
		res = self.client().post('/books', json={'search': 'Novel'})
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertTrue(data['total_books'])
		self.assertEqual(len(data['books']), 4)

	def test_get_book_search_without_results(self):
		res = self.client().post('/books', json={'search': 'applejacks'})
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertEqual(data['total_books'], 0)
		self.assertEqual(len(data['books']), 0)



    """def test_given_behavior(self):
            Largest body of test
			Various tests
			should all start with test_ 
			should include doc string about the purpose of the test
        res = self.client().get('/')

        self.assertEqual(res.status_code, 200)"""

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()