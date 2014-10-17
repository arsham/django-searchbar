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
    ....
```

You can also change the form method:

```python
    search_bar = SearchBar(request, ['name', 'age'], method='get')
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
                ('m', 'Male'),
                ('f', 'Female'),
            ), #Same format as django's forms
            'required': True, #Optional, default is false
        },
    ])

```
