django-searchbar
============

# About

A simple search bar and view handler to validate and get the results

## Usage

In your view:

<pre>
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
</pre>
