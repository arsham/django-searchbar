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
                assert isinstance(field, (str, dict)), 'fields should be string types, but you provided %s' % type(field)
                if isinstance(field, dict):
                    assert 'label' in field, 'You should provide a label'
                    if 'choices' in field:
                        assert isinstance(field['choices'], (list, tuple)), 'You should provide a label'

        super(SearchBarForm, self).__init__(data)
        for field in fields:

            if isinstance(field, str):

                label = field.replace('-', ' ').replace('_', ' ').title()
                self.fields[field] = forms.CharField(label=label, required=False)

            elif isinstance(field, dict):

                label = field['label'].replace('-', ' ').replace('_', ' ').title()
                required = field.get('required', False)

                if 'choices' in field:
                    self.fields[field['label']] = forms.ChoiceField(label=label, choices=field['choices'], required=required)
                elif 'widget' in field:
                    self.fields[field['label']] = forms.CharField(label=label, required=required, widget=field['widget'])
                else:
                    self.fields[field['label']] = forms.CharField(label=label, required=required)
