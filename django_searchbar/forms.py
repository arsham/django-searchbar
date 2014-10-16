from django import forms


class SearchBarForm(forms.Form):

    """
    This is the form that ends up in your templates
    """

    def __init__(self, data, fields):

        from django_searchbar.utils import listify
        fields = listify(fields)

        if __debug__:
            for field in fields:
                assert isinstance(field, str), 'fields should be string types, but you provided %s' % type(field)

        super(SearchBarForm, self).__init__(data)
        for field in fields:
            self.fields[field] = forms.CharField(label=field, required=False)
