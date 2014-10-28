from django.test import TestCase
from django.test.client import Client
from django.test.client import RequestFactory
from django.forms import fields
from django.db.models import Q
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
        self.assertRaises(AssertionError, SearchBar, ['name'], request)
        self.assertIsInstance(SearchBar(fields=['name'], request=request), SearchBar)
        self.assertIsInstance(SearchBar(request, ['name']), SearchBar)
        self.assertIsInstance(SearchBar(request, 'name'), SearchBar)

    def testInitializationWithChoices(self):
        request = RequestFactory().get('/')
        self.assertIsInstance(SearchBar(request, {'label': 'name'}), SearchBar)
        self.assertIsInstance(SearchBar(request, {
            'label': 'name',
            'choices': ({'aaa': 'bbb'},),
        }), SearchBar)
        self.assertIsInstance(SearchBar(request, {
            'label': 'name',
            'choices': (('aaa', 'bbb'),),
        }), SearchBar)
        self.assertRaises((AssertionError, ValueError), SearchBar, request, {
            'labels': 'name',
            'choices': (('aaa', 'bbb'),),
        })
        self.assertRaises((AssertionError, ValueError), SearchBar, request, {
            'choices': (('aaa', 'bbb'),),
        })
        self.assertRaises((AssertionError, ValueError), SearchBar, request, {
            'label': 'name',
            'choices': None,
        })

    def testChoicesReturnValues(self):
        request = RequestFactory().get('/?name=arsham')
        search_bar = SearchBar(request, {
            'label': 'name',
            'choices': (
                ('arsham', 'Arsham Shirvani'),
                {'ivan': 'Ivan'},
            ),
        })
        search_bar.is_valid()
        self.assertEqual(search_bar['name'], 'arsham')
        self.assertEqual(search_bar.get('name'), 'arsham')

        request = RequestFactory().get('/?name2=arsham')
        search_bar = SearchBar(request, {
            'label': 'name',
            'choices': (
                ('arsham', 'Arsham Shirvani'),
                {'ivan': 'Ivan'},
            ),
        })
        search_bar.is_valid()
        self.assertEqual(search_bar['name'], '')

    def testRequiredFields(self):
        request = RequestFactory().get('/?name2=arsham')
        search_bar = SearchBar(request, {
            'label': 'name',
            'choices': (
                ('arsham', 'Arsham Shirvani'),
            ),
            'required': False,
        })

        self.assertTrue(search_bar.is_valid())
        self.assertFalse(search_bar.form.fields['name'].required)

        request = RequestFactory().get('/?name2=arsham')
        search_bar = SearchBar(request, {
            'label': 'name',
            'choices': (
                ('arsham', 'Arsham Shirvani'),
            ),
            'required': True,
        })

        self.assertFalse(search_bar.is_valid())
        self.assertTrue(search_bar.form.fields['name'].required)

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
        self.assertTrue(search_bar.is_valid())
        self.assertFalse(search_bar.is_valid('name'))

        request = RequestFactory().get('/?name=123')
        search_bar = SearchBar(request, ['name', 'age'])
        self.assertTrue(search_bar.is_valid())
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

    def testOutputString(self):
        request = RequestFactory().get('/')
        search_bar = SearchBar(request, ['name', 'age'])
        self.assertIn('id="id_name"', str(search_bar))
        self.assertIn('name="name"', str(search_bar))

        self.assertIn('csrfmiddlewaretoken', str(search_bar.as_form()))
        self.assertIn('<form', str(search_bar.as_form()))
        self.assertIn('</form>', str(search_bar.as_form()))

    def testGetFilters(self):
        request = RequestFactory().get('/?username=arsham&email=this_is_an_email')
        search_bar = SearchBar(request, ['username', 'email'])
        search_bar.is_valid()
        self.assertIsInstance(search_bar.get_filters(), Q)
        self.assertIn("'username'", str(search_bar.get_filters()))
        self.assertNotIn("'username__iexact'", str(search_bar.get_filters()))
        self.assertIn("'email'", str(search_bar.get_filters()))
        self.assertIn("'username__icontains'", str(search_bar.get_filters(lookup_string='icontains')))
        self.assertIn("'email__icontains'", str(search_bar.get_filters(lookup_string='icontains')))
        self.assertIn("(AND: ", str(search_bar.get_filters()))
        self.assertIn("arsham", str(search_bar.get_filters()))
        self.assertIn("this_is_an_email", str(search_bar.get_filters()))
        self.assertNotIn('(OR:', str(search_bar.get_filters()))

        search_bar = SearchBar(request, ['username', 'email'])
        search_bar.is_valid()
        self.assertIn("'username'", str(search_bar.get_filters('username')))
        self.assertNotIn("'email__exact'", str(search_bar.get_filters('username')))

        search_bar = SearchBar(request, ['username', 'email', 'age'])
        search_bar.is_valid()
        self.assertIn("'username'", str(search_bar.get_filters('username', 'age')))
        self.assertIn("'username__icontains'", str(search_bar.get_filters('username', 'age', lookup_string='icontains')))
        self.assertIn("'email'", str(search_bar.get_filters('username', 'email')))
        self.assertIn("'username'", str(search_bar.get_filters('username', 'email')))
        self.assertNotIn("'age'", str(search_bar.get_filters('username', 'email')))

    def testEmptyFilters(self):
        request = RequestFactory().get('/')
        search_bar = SearchBar(request, ['username', 'email'])
        search_bar.is_valid()
        self.assertEqual("(AND: )", str(search_bar.get_filters()))

    def testReplacementsDictionary(self):
        request = RequestFactory().get('/?name=arsham&age=6')
        search_bar = SearchBar(request, ['name'], replacements={'name': 'username'})
        search_bar.is_valid()
        self.assertIn("'username'", str(search_bar.get_filters()))
        self.assertNotIn("'user__'", str(search_bar.get_filters()))

    def testReplacementsCallable(self):
        request = RequestFactory().get('/?name=arsham&age=6')
        search_bar = SearchBar(request, ['name'], replacements={'name': lambda x: 'username'})
        search_bar.is_valid()
        self.assertIn("'username'", str(search_bar.get_filters()))
        self.assertNotIn("'user__'", str(search_bar.get_filters()))

    def testIgnoreList(self):
        request = RequestFactory().get('/?gender=m')
        search_bar = SearchBar(request, [{
            'label': 'gender',
            'choices': (
                ('none', '---'),
                ('m', 'Male'),
                ('f', 'Female'),
            ),
            'ignore_list': ['none']
        }])
        search_bar.is_valid()
        self.assertIn("'gender'", str(search_bar.get_filters()))

        request = RequestFactory().get('/?gender=none')
        search_bar = SearchBar(request, [{
            'label': 'gender',
            'choices': (
                ('none', '---'),
                ('m', 'Male'),
                ('f', 'Female'),
            ),
            'ignore_list': ['none']
        }])
        search_bar.is_valid()
        self.assertNotIn("'gender'", str(search_bar.get_filters()))

    def testAddFields(self):

        request = RequestFactory().get('/?name=asdasd')
        search_bar = SearchBar(request, ['name'])

        search_bar.is_valid()

        self.assertNotIn('asd1', search_bar)
        search_bar['asd1'] = 'asd'
        self.assertIn('asd1', search_bar)

        search_bar['asd2'] = ({'aaa': 'bbb'},)
        self.assertIn('asd2', search_bar)

        search_bar['asd3'] = {'label': 'ASD', 'choices': ({'aaa': 'bbb'},)}
        self.assertIn('asd3', search_bar)


    def testPopFields(self):

        request = RequestFactory().get('/?name=asdasd&age=10&other=asdasd')
        search_bar = SearchBar(request, ['name', 'age', 'other'])

        search_bar.is_valid()

        self.assertNotIn('asd', search_bar)

        search_bar.pop('age')
        self.assertNotIn('age', search_bar)

        search_bar.pop('other')
        self.assertNotIn('other', search_bar)

        self.assertNotIn('ggg', search_bar)


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

    def testInstantiateWithChoices(self):

        self.assertIsInstance(SearchBarForm({}, {
            'label': 'name',
            'choices': ({'aaa': 'bbb'},),
        }), SearchBarForm)
        self.assertRaises((AssertionError, ValueError), SearchBarForm, {}, {
            'labels': 'name',
            'choices': (('aaa', 'bbb'),),
        })
        self.assertRaises((AssertionError, ValueError), SearchBarForm, {}, {
            'choices': (('aaa', 'bbb'),),
        })
        self.assertRaises((AssertionError, ValueError), SearchBarForm, {}, {
            'label': 'name',
            'choices': None,
        })

    def testChoicesFieldHasADifferentWidget(self):

        search_bar = SearchBarForm({}, ['username', {
            'label': 'name',
            'choices': ({'aaa': 'bbb'},),
        }])
        self.assertIsInstance(search_bar.fields['username'], fields.CharField)
        self.assertIsInstance(search_bar.fields['name'], fields.ChoiceField)


class IntegrationTestCase(TestCase):

    def setUp(self):

        self.c = Client()

    def testCreatingFormWidgetOnOutput(self):
        response = self.c.get('/?name=arsham&age=6&order_by=asc')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name,
                         'django_searchbar/test.html')

        form = response.context['search_bar']
        self.assertIn('<label for=', str(form))
        self.assertIn('id="id_name"', str(form))
        self.assertIn('name="name"', str(form))
        self.assertIn('type="text"', str(form))
        self.assertIn('value="arsham"', str(form))
        self.assertIn('<select id="id_order_by"', str(form))
        self.assertIn('name="order_by"', str(form))
        self.assertIn('<option value="asc"', str(form))
        self.assertIn('selected="selected"', str(form))
        self.assertEqual(str(form).count('<option'), 2)
        self.assertEqual(str(form).count('<select'), 1)
        self.assertEqual(str(form).count('</option>'), 2)

        form.is_valid()

        self.assertEqual(form['name'], 'arsham')
        self.assertEqual(form['age'], '6')
        self.assertEqual(form['order_by'], 'asc')
