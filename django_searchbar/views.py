from django.shortcuts import render
from django_searchbar.utils import SearchBar


def homepage(request):

    search_bar = SearchBar(request, [
        'name', {
            'label': 'age',
        },
        {
            'label': 'order_by',
            'choices': (
                ('asc', 'ASC'),
                ('desc', 'DESC'),
            ),
        }
    ])

    return render(request, 'django_searchbar/test.html', {
        'search_bar': search_bar,
    })
