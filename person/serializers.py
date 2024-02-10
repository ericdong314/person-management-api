from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model


age_field = serializers.ReadOnlyField(source='get_age')
filter_person_fields = ['url', 'id', 'first_name', 'last_name', 
                        'email', 'phone', 'date_of_birth', 'age']

class PersonSerializer(serializers.HyperlinkedModelSerializer):
    age = age_field
    
    # Hash password
    def validate_password(self, value):
        return make_password(value)
    
    class Meta:
        model = get_user_model()
        fields = filter_person_fields + ['username', 'password', 'is_staff']
    

class FilterPersonSerializer(serializers.HyperlinkedModelSerializer):
    age = age_field

    class Meta:
        model = get_user_model()
        fields = filter_person_fields