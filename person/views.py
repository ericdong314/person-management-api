from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets, permissions, generics
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
        age = self.request.query_params.get("age", "")
        persons = get_user_model().objects.filter(
            first_name__contains=first_name,
            last_name__contains=last_name
        )
        if age:
            persons = [p for p in persons if p.age == int(age)]
        return persons 
    