from django.db import models
from django.contrib.auth.models import User

#all models are indexed for efficient querying

#model to store information about professors
class Professor(models.Model):
    #ID for each professor
    professor_id = models.CharField(max_length=10, unique=True, primary_key=True)  
    #name of the professor
    name = models.CharField(max_length=255, db_index=True)  

    def __str__(self):
        return self.name 

#model to store information about modules 
class Module(models.Model):
    #unique module code
    code = models.CharField(max_length=10, unique=True, primary_key=True) 
    # Name of the module
    name = models.CharField(max_length=255, db_index=True)  

    def __str__(self):
        return self.name 

#model to represent instances of a module 
class ModuleInstance(models.Model):
    #link each instance to a module
    module = models.ForeignKey(Module, on_delete=models.CASCADE)  
    #multiple professors teaching a single module instance
    professors = models.ManyToManyField(Professor)  
    #year the module instance is being offered
    year = models.IntegerField(db_index=True)  
    #semester in which the module instance is being offered
    semester = models.IntegerField()  

    def __str__(self):
        return f"{self.module.name} ({self.year} - Semester {self.semester})"

# model to store ratings for professors within specific module instances
class Rating(models.Model):
    #user who submits the rating
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    #professor being rated
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)  
    #module instance where the professor was rated
    module_instance = models.ForeignKey(ModuleInstance, on_delete=models.CASCADE)  
    #rating value 
    rating = models.IntegerField()  

    class Meta:
        #constraints to ensure rating values are between 1 and 5
        constraints = [
            models.CheckConstraint(check=models.Q(rating__gte=1) & models.Q(rating__lte=5), name='valid_rating_range'),
        ]
        #ensures a user can only submit one rating per professor per module instance
        unique_together = ('user', 'professor', 'module_instance')  
