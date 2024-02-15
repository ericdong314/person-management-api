from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from rest_framework import mixins, viewsets, permissions, generics, exceptions
from person.serializers import PersonSerializer, FilterPersonSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class PersonViewSet(viewsets.ModelViewSet):
    serializer_class = PersonSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = get_user_model().objects.all()


class PersonFilter(filters.FilterSet):
    first_name = filters.CharFilter("first_name", "contains")
    last_name  = filters.CharFilter("last_name",  "contains")
    max_age    = filters.NumberFilter(method="filter_max_age")
    min_age    = filters.NumberFilter(method="filter_min_age")

    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "max_age", "min_age"]

    def filter_max_age(self, query_set, name, value):
        min_date_of_birth = now().date() - relativedelta(years=(value + 1))
        return query_set.filter(date_of_birth__gt=min_date_of_birth)
    
    def filter_min_age(self, query_set, name, value):
        max_date_of_birth = now().date() - relativedelta(years=value)
        return query_set.filter(date_of_birth__lte=max_date_of_birth)


class FilterPersonViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = get_user_model().objects.all()
    serializer_class =  FilterPersonSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = PersonFilter
