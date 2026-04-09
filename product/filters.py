import django_filters
from django_filters.rest_framework import FilterSet
from product.models import Product


class ProductFilter(FilterSet):

    # allow multiple category ids
    category_id = django_filters.BaseInFilter(
        field_name="category__id",
        lookup_expr="in"
    )

    # price filters
    price__gt = django_filters.NumberFilter(field_name="price", lookup_expr="gt")
    price__lt = django_filters.NumberFilter(field_name="price", lookup_expr="lt")

    class Meta:
        model = Product
        fields = ['category_id', 'price__gt', 'price__lt']