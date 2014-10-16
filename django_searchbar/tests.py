from unittest import TestCase
from django.test.client import Client
from django.test.client import RequestFactory
from django_searchbar.utils import SearchBar, listify
from django_searchbar.forms import SearchBarForm


class UtilsTestCase(TestCase):

    def testListify(self):
        self.assertIsInstance(listify('name'), (list, tuple))
        self.assertIsInstance(listify(['name']), (list, tuple))
        self.assertNotIsInstance(listify('name'), str)

    def testInitializationFailsWithWrongTypes(self):

        request = RequestFactory().get('/')
        self.assertRaises(TypeError, SearchBar)
        self.assertRaises(AssertionError, SearchBar, 1)
        self.assertRaises(AssertionError, SearchBar, request, [[]])
        self.assertRaises(AssertionError, SearchBar, request, [None])
        SearchBar(request, ['name'])
        SearchBar(request, 'name')

    def testIsValidMethodGet(self):
        request = RequestFactory().get('/?name=123')
        search_bar = SearchBar(request, 'name')
        self.assertTrue(search_bar.is_valid())
        self.assertTrue(search_bar.is_valid('name'))

        request = RequestFactory().get('/?name=123&age=6&error=info')
        search_bar = SearchBar(request, ['name', 'age'])
        self.assertTrue(search_bar.is_valid())
        self.assertTrue(search_bar.is_valid('name'))
        self.assertTrue(search_bar.is_valid('age'))
        self.assertTrue(search_bar.is_valid('age', 'name'))

        request = RequestFactory().get('/?name=123')
        search_bar = SearchBar(request, ['name', 'age'])
        self.assertTrue(search_bar.is_valid('name'))

    def testIsValidMethodPost(self):
        request = RequestFactory().post('/', {'name': 123})
        search_bar = SearchBar(request, 'name')
        self.assertTrue(search_bar.is_valid())
        self.assertTrue(search_bar.is_valid('name'))

        request = RequestFactory().post('/', {'name': 123, 'age': 6, 'error': 'info'})
        search_bar = SearchBar(request, ['name', 'age'])
        self.assertTrue(search_bar.is_valid())
        self.assertTrue(search_bar.is_valid('name'))
        self.assertTrue(search_bar.is_valid('age'))
        self.assertTrue(search_bar.is_valid('age', 'name'))

        request = RequestFactory().post('/', {'name': 123})
        search_bar = SearchBar(request, ['name', 'age'])
        self.assertTrue(search_bar.is_valid('name'))

    def testIsValidMethodFails(self):
        request = RequestFactory().get('/')
        search_bar = SearchBar(request, 'name')
        self.assertFalse(search_bar.is_valid())
        self.assertFalse(search_bar.is_valid('name'))

        request = RequestFactory().get('/?name=123')
        search_bar = SearchBar(request, ['name', 'age'])
        self.assertFalse(search_bar.is_valid())
        self.assertFalse(search_bar.is_valid('age'))
        self.assertFalse(search_bar.is_valid('age', 'name'))

    def testGettingBackTheValue(self):
        request = RequestFactory().get('/?name=arsham&age=6')
        search_bar = SearchBar(request, ['name', 'age'])
        search_bar.is_valid()
        self.assertEqual(search_bar['name'], 'arsham')
        self.assertEqual(search_bar['age'], '6')

        request = RequestFactory().get('/?name=&age=')
        search_bar = SearchBar(request, ['name', 'age'])
        search_bar.is_valid()
        self.assertEqual(search_bar['name'], '')
        self.assertEqual(search_bar['age'], '')


class FormsTestCase(TestCase):

    def testInitializationFailsWithWrongTypes(self):
        self.assertRaises((AssertionError, TypeError), SearchBarForm)
        self.assertRaises((AssertionError, TypeError), SearchBarForm, 6)
        self.assertRaises((AssertionError, TypeError), SearchBarForm, ['666', 6])

    def testStuffThatAreNotInFormShouldFail(self):
        form = SearchBarForm({}, ['name', 'age'])
        self.assertIn('name', form.fields)
        self.assertIn('age', form.fields)
        self.assertNotIn('blah', form.fields)

    def testFormOutput(self):
        form = SearchBarForm({}, ['name', 'age'])
        self.assertIn('id_age', str(form))
        self.assertIn('id_name', str(form))


class IntegrationTestCase(TestCase):

    def setUp(self):

        self.c = Client()

    def testInboxEmpty(self):
        response = self.c.get('/?name=arsham&age=6')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name,
                         'django_searchbar/test.html')

        form = response.context['search_bar']
        form.is_valid()

        self.assertEqual(form['name'], 'arsham')
        self.assertEqual(form['age'], '6')
