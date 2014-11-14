django-searchbar
============

# About

A simple search bar and view handler to validate and get the results

## Usage

In your view:

```python
def my_view(request):
    search_bar = SearchBar(request, ['name', 'age'])

    #When the form is coming from posted page
    if search_bar.is_valid():
        my_name = search_bar['name']
    ....

    #If your url comes as: "?name=my_name" and you don't care about the age, do this instead:
    if search_bar.is_valid('name'):
        my_name = search_bar['name']
        #If you need to apply name to your queryset:
        Model.objects.filter(name__contains=my_name)
    ....
```

Or if you prefer Class Based Views:

```python
from django.views.generic import ListView
from django_searchbar.mixins import SearchBarViewMixin

class MyView(SearchBarViewMixin, ListView):
    searchbar_fields = ['name']
    ....
```

and that's about it! The search bar get's validated on it's own, and it will use the value of 'name' in your queryset automatically.
You can access the search bar in your template by (It's automatically is injected into your context):

```python
{{ search_bar }}
```

You can also change the form method, choices are 'get' and 'post':

```python
    search_bar = SearchBar(request, ['name', 'age'], method='get')
```

In CBV:

```python
class MyView(SearchBarViewMixin, ListView):
    searchbar_fields = ['name']
    searchbar_method = 'get'
```

## Advanced Usage

Notice: This is as far as it goes, if you need more advanced techniques you should use django's forms.

If you need to show choices or set a field required:

```python
def my_view(request):
    search_bar = SearchBar(request, [
        'name',
        {
            'label': 'age',
        },
    ]) # this is the same as above, but....

    search_bar = SearchBar(request, [
        'name',
        {
            'label': 'age',
            'required': True,
        },
    ])# Will fail the validation if user don't provide a value for age

    #If you need choices, do:
    search_bar = SearchBar(request, [
        'name',
        {
            'label': 'gender',
            'choices': (
                ('none', 'N/A')
                ('m', 'Male'),
                ('f', 'Female'),
            ), #Same format as django's forms
            'ignore_list': ['none'] #Ignores in query filters if the value is 'none' (as above)
            'required': True, #Optional, default is false
        },
    ])

    #If you need custom widget:
    search_bar = SearchBar(request, [
        'name',
        {
            'label': 'age',
            'required': True,
            'widget': forms.Textarea(attrs={'placeholder': 'Enter your name here..'})
        },
    ])
```

Or in CBV:

```python
class MyView(SearchBarViewMixin, ListView):
    searchbar_fields = [
        'name',
        {'label': 'age', 'required': True},
        {
            'label': 'gender',
            'choices': (
                ('none', 'N/A')
                ('m', 'Male'),
                ('f', 'Female'),
            ), #Same format as django's forms
            'ignore_list': ['none'] #Ignores in query filters if the value is 'none' (as above)
            'required': True, #Optional, default is false
        },
    ]
```

You can also define a replacement dictionary/callback, which transforms your input to something you can actually use in your db.model queries after getting filters (get_filters)

```python
    search_bar = SearchBar(request, ['username'], replacement={'username': 'user__username'})
```

or a bit smarter:

```python
    def replacement(item):
        return {
            'username': 'user__username',
            'foo': 'bar',
        }.get(item, 'user__username')

    search_bar = SearchBar(request, ['username'], replacement=replacement)
```

In CBV:

```python
class MyView(SearchBarViewMixin, ListView):
    searchbar_replacements = {
        'username': 'user__username',
    }
    #or using above function:
    searchbar_replacements = replacement

```

## Recipes

If you have a field you are using in various places, e.g. if you have ordering on some of your searchbars, do this:

```python
from django_searchbar.utils import SearchBar


class OrderingSearchBar(SearchBar):

    def __init__(self, request, choices, replacements={}, fields=None, method='post'):

        ...do some checks here...

        self.__choices = (('none', '----'),) + choices
        self.__replacements = replacements
        fields.extend([{
            'label': 'order_by',
            'choices': self.__choices,
        }, {
            'label': 'direction',
            'choices': (
                ('asc', 'ASC'),
                ('desc', 'DESC'),
            ),
        },
        ])

        super().__init__(request=request, fields=fields, method=method)

    def __getitem__(self, index):
        if index == 'order_by':

            exam_dict = {}
            for choice in self.__choices:
                if choice[0] is 'none':
                    exam_dict[choice[0]] = False
                else:
                    exam_dict[choice[0]] = self.__replacements.get(choice[0], choice[0])

            order_by = exam_dict.get(self.form.cleaned_data['order_by'])

            if order_by and order_by != 'none':
                direction = {
                    'asc': '',
                    'desc': '-',
                }.get(self['direction'], '')

                return "%s%s" % (direction, order_by)

            return False

        else:
            return super().__getitem__(index)


#Now the mixin
class OrderingSearchBarViewMixin(SearchBarViewMixin):

    def get_searchbar(self, request):
         ...do some checks here...
        return OrderingSearchBar(
            request=request,
            choices=self.searchbar_choices,
            fields=self.searchbar_fields,
            replacements=self.searchbar_replacements,
            method=self.searchbar_method)

    def get(self, request, *args, **kwargs):

        search_obj = self.get_searchbar(request)
        if search_obj.is_valid() and search_obj.get_ordering():
                self.queryset = self.queryset.order_by(search_obj.get_ordering())

        return super().get(request, *args, **kwargs)

```

Now in your view you can do this:

```python
    choices = (
        ('username', 'Username'),
    )
    replacements = {
        'username': 'user__username__icontains',
    }

    search_obj = OrderingSearchBar(request, fields=['username'], choices=choices, replacements=replacements)
    people = Person.objects.all()

    if search_obj.is_valid():
        people = people.filter(user__username__icontains=search_obj['username'])
        #Or
        people = people.filter(search_obj.get_filters())

```

In CBV:

```python
class MyView(SearchBarViewMixin, ListView):
    searchbar_choices = (
        ('username', 'Username'),
    )
    searchbar_replacements = {
        'username': 'user__username__icontains',
    }

```
