if __debug__:
    from django.http import HttpRequest

from django_searchbar.forms import SearchBarForm


def listify(item):
    """
    A simple function to create a list if item is not a list or a tuple
    @type item: str|iterable
    @return list
    """

    if not isinstance(item, (list, tuple)):
        item = [item]
    return item


class SearchBar:

    """
    Usage:
        In your view, do this:
        def my_view(request):
            search_bar = SearchBar(request, ['name', 'age'])
            if search_bar.is_valid():
                name_value = search_bar['name']
    """

    def __init__(self, request, fields=None):

        assert isinstance(request, HttpRequest), 'request should be an instance of the HttpRequest object'
        assert isinstance(fields, (type(None), list, tuple, str)), 'fields should be None, list or a tuple containing strings'

        if __debug__ and isinstance(fields, (list, tuple)):
            for item in fields:
                assert isinstance(item, str), '%s should be a string' % item

        if fields:
            fields = listify(fields)

            self.form = SearchBarForm(request.GET or request.POST, fields=fields)

        self.request = request
        self.__fields = fields

    def is_valid(self, *args, **kwargs):
        """
        Validates the SearchBar instance.
        All required argument you pass here, should end up in request results to pass.
        @return bool
        """
        if not self.__fields:
            return False

        form_validation = self.form.is_valid()

        if form_validation and args:
            args = listify(args)
            form_validation &= all(self.form.cleaned_data.get(item, '') != '' for item in args)

        elif form_validation and self.__fields:
            form_validation &= all(self.form.cleaned_data.get(item, '') != '' for item in self.__fields)

        return form_validation

    def __getitem__(self, index):
        return self.form.cleaned_data[index]

    def __str__(self):
        return str(self.form)
