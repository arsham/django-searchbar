# -*- coding: utf-8 -*-
from .utils import SearchBar


class SearchBarViewMixin:

    """
    A Class Based View Mixin to use SearchBar
    """
    searchbar_method = 'post'

    def get_searchbar(self, request):
        return SearchBar(request, self.searchbar_fields, self.replacements, self.searchbar_method)

    def dispatch(self, request, *args, **kwargs):
        assert hasattr(self, 'searchbar_fields'), 'You should provide searchbar_fields attribute in your class'
        self.replacements = getattr(self, 'searchbar_replacements', {})
        self.searchbar_obj = self.get_searchbar(request)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        search_obj = self.get_searchbar(request)
        if search_obj.is_valid():
            self.queryset = self.queryset.filter(search_obj.get_filters())

        if hasattr(super(), 'post'):
            return super().post(request, *args, **kwargs)
        else:
            return super().get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        search_obj = self.get_searchbar(request)
        if search_obj.is_valid():
            self.queryset = self.queryset.filter(search_obj.get_filters())

        return super().get(request, *args, **kwargs)
