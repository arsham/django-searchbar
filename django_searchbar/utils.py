if __debug__:
    from django.http import HttpRequest

import collections
from django_searchbar.forms import SearchBarForm
from django import forms
from django.middleware import csrf
from django.utils.safestring import mark_safe
from django.db.models import Q


def listify(item):
    """
    A simple function to create a list if item is not a list or a tuple
    @type item: str|iterable
    @return list
    """

    if not isinstance(item, (list, tuple)):
        item = [item]
    return item


class SearchBar(collections.MutableMapping):

    """
    Usage:
        In your view, do this:
        def my_view(request):
            search_bar = SearchBar(request, ['name', 'age'])
            if search_bar.is_valid():
                name_value = search_bar['name']
    """

    def __init__(self, request, fields=None, replacements={}, method='post'):

        assert isinstance(request, HttpRequest), 'request should be an instance of the HttpRequest object'
        assert isinstance(fields, (type(None), list, tuple, str, dict)), 'fields should be None, list or a tuple containing strings'
        assert isinstance(replacements, (dict, collections.Callable)), 'fields should be dictionary or a callable'

        if __debug__:
            def check_dict(item):
                assert 'label' in item, 'Your fields should have a label'
                if 'choices' in item:
                    assert isinstance(item['choices'], collections.Iterable), 'Your choices should be a dict'

            if isinstance(fields, (list, tuple)):
                for item in fields:
                    assert isinstance(item, (str, dict)), '%s should be a string or a dictionary containing label' % item
                    if isinstance(item, dict):
                        check_dict(item)
            elif isinstance(fields, dict):
                check_dict(fields)

        if fields:
            fields = listify(fields)

        self.request = request
        self.replacements = replacements
        self.fields = fields
        self.old_fields = None
        self.action = ''
        self.method = method.lower().strip()
        self.__form = None
        self.errors = []

    @property
    def form(self):
        if not self.__form and self.old_fields != self.fields:
            self.__form = SearchBarForm(self.request.GET or self.request.POST, fields=self.fields)
            self.__form.is_valid()
            self.old_fields = self.fields

        return self.__form

    def is_valid(self, *args, **kwargs):
        """
        Validates the SearchBar instance.
        All required argument you pass here, should end up in request results to pass.
        @return bool
        """

        def check_validation(self, item):
            if isinstance(item, dict):
                if item.get('required', False) and self.form.cleaned_data.get(item['label'], '') == '':
                    self.errors.append('%s is empty' % item['label'])
            elif isinstance(item, str):
                if item not in self.form.cleaned_data:
                    self.errors.append('Our form didn\'t validate %s' % item)

        if not self.fields:
            self.errors.append('There is no field set')
            return False

        form_validation = self.form.is_valid()

        if form_validation and args:
            args = listify(args)
            if not all(self.form.cleaned_data.get(item, '') != '' for item in args):
                self.errors.append('Values in form was failed by form itself')

        elif form_validation and self.fields:
            for item in self.fields:
                check_validation(self, item)
        else:
            self.errors.append('Values in form was failed by form itself')

        return not self.errors

    def as_form(self):
        csrf_ = ''
        if self.method == 'post':
            csrf_ = "<input type='hidden' name='csrfmiddlewaretoken' value='{0}' />".format(csrf.get_token(self.request))
        submit_button = '<input type="submit" value="submit" />'
        return_string = "<form method='%s' action='%s'>%s %s %s</form>" % (self.method, self.action, csrf_, self, submit_button)
        return mark_safe(return_string)

    def get_filters(self, *args, lookup_string=''):
        """
        Returns a Q object based on all the input from query term
        @param lookup_string: adds this ``lookup_string`` to query lookup of all fields
        @param args: if provided, items you need to be in queryset. otherwise it's everything
        """
        filters = Q()
        lookup_string = lookup_string.lower().strip()

        if args:
            __fields = [k for k in self.fields if k in args]
        else:
            __fields = self.fields

        for field in __fields:

            ignore_list = []
            if isinstance(field, dict):
                ignore_list = field.get('ignore_list', [])
                field = field['label']

            if self[field] and not self[field] in ignore_list:
                replacement = self.replacements.get(field, field)
                if isinstance(replacement, collections.Callable):
                    replacement = replacement(field)

                if lookup_string:
                    field_name = "{field}__{method}".format(field=replacement, method=lookup_string)
                else:
                    field_name = replacement

                filters &= Q(**{field_name: self[field]})
        return filters

    def __contains__(self, key):

        return key in self.form.fields

    def __getitem__(self, key):

        if key == 'as_form':
            return self.as_form()

        return self.form.cleaned_data.get(key, '')

    def __setitem__(self, key, value):

        if isinstance(value, str):

            self.form.fields[key] = forms.CharField(label=value, required=False)

        elif isinstance(value, (list, tuple)):

            label = key.replace('-', ' ').replace('_', ' ').title()
            self.form.fields[key] = forms.ChoiceField(label=label, choices=value, required=False)

        elif isinstance(value, dict):

            required = value.get('required', False)

            if 'label' in value:
                label = value['label']
            else:
                label = key.replace('-', ' ').replace('_', ' ').title()

            self.form.fields[key] = forms.ChoiceField(label=label, choices=value, required=required)

    def __delitem__(self, key):

        self.form.fields.pop(key)

    def __iter__(self):

        for name in self.form.fields:
            yield self.form[name]

    def __len__(self):

        return len(self.form.fields)

    def __str__(self):

        return str(self.form)
