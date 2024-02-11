from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets, permissions, generics, exceptions
from person.serializers import PersonSerializer, FilterPersonSerializer


class PersonViewSet(viewsets.ModelViewSet):
    serializer_class = PersonSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = get_user_model().objects.all()


class FilterPersonViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class =  FilterPersonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        first_name = self.request.query_params.get("first_name", "")
        last_name = self.request.query_params.get("last_name", "")
        min_age = self.request.query_params.get("min_age", "")
        max_age = self.request.query_params.get("max_age", "")
        persons = get_user_model().objects.filter(
            first_name__contains=first_name,
            last_name__contains=last_name
        )
        if min_age:
            if not str.isdecimal(min_age):
                raise exceptions.ValidationError({"min_age": ["min_age must be an integer"]})
            persons = [p for p in persons if p.get_age() and p.get_age() >= int(min_age)]
        if max_age:
            if not str.isdecimal(max_age):
                raise exceptions.ValidationError({"max_age": ["max_age must be an integer"]})
            persons = [p for p in persons if p.get_age() and p.get_age() <= int(max_age)]
        return persons
