from rest_framework import serializers  
from .models import Rating, ModuleInstance, Professor  

#this file is responsible for converting Django models into JSON responses 

class ProfessorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Professor model
    Converts Professor instances into JSON format
    """
    class Meta:
        model = Professor  
        fields = ['professor_id', 'name']  

class ModuleInstanceSerializer(serializers.ModelSerializer):
    """
    Serializer for the ModuleInstance model.
    This serializer includes a nested representation of professors.
    """
    professors = ProfessorSerializer(many=True, read_only=True) 

    class Meta:
        model = ModuleInstance  
        fields = ['module', 'year', 'semester', 'professors']  

class RatingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Rating model.
    Converts Rating instances into JSON format and handles input validation.
    """
    class Meta:
        model = Rating  
        fields = ['user', 'professor', 'module_instance', 'rating']  
