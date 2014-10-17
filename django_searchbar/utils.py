if __debug__:
    from django.http import HttpRequest

from django_searchbar.forms import SearchBarForm
from django.middleware import csrf
from django.utils.safestring import mark_safe


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

    def __init__(self, request, fields=None, method='post'):

        assert isinstance(request, HttpRequest), 'request should be an instance of the HttpRequest object'
        assert isinstance(fields, (type(None), list, tuple, str, dict)), 'fields should be None, list or a tuple containing strings'

        if __debug__ and isinstance(fields, (list, tuple)):
            for item in fields:
                assert isinstance(item, (str, dict)), '%s should be a string or a dictionary containing label' % item

        if fields:
            fields = listify(fields)

            self.form = SearchBarForm(request.GET or request.POST, fields=fields)

        self.request = request
        self.__fields = fields
        self.action = ''
        self.method = method.lower().strip()

    def is_valid(self, *args, **kwargs):
        """
        Validates the SearchBar instance.
        All required argument you pass here, should end up in request results to pass.
        @return bool
        """

        def check_validation(self, item):
            if isinstance(item, dict):
                if item.get('required', False) and self.form.cleaned_data.get(item['label'], '') == '':
                    return False
            elif isinstance(item, str):
                if self.form.cleaned_data.get(item, '') == '':
                    return False

            return True

        if not self.__fields:
            return False

        form_validation = self.form.is_valid()

        if form_validation and args:
            args = listify(args)
            form_validation = all(self.form.cleaned_data.get(item, '') != '' for item in args)

        elif form_validation and self.__fields:
            for item in self.__fields:
                if not check_validation(self, item):
                    form_validation = False
                    break

        return form_validation

    def as_form(self):
        csrf_ = ''
        if self.method == 'post':
            csrf_ = "<input type='hidden' name='csrfmiddlewaretoken' value='{0}' />".format(csrf.get_token(self.request))
        submit_button = '<input type="submit" value="submit" />'
        return_string = "<form method='%s' action='%s'>%s %s %s</form>" % (self.method, self.action, csrf_, self, submit_button)
        return mark_safe(return_string)

    def __getitem__(self, index):
        if index == 'as_form':
            return self.as_form()

        return self.form.cleaned_data.get(index, '')

    def __str__(self):
        return str(self.form)
