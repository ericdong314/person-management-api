from django.shortcuts import render
from .models import Products 
import django_filters


class ProductFilter(django_filters.FilterSet):
    name = CharFilter("name", "iexact")

    class Meta:
        model = Product
        fields = ["name", "release_date"]
