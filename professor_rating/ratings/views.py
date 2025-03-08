from rest_framework.permissions import IsAuthenticated  
from rest_framework.decorators import permission_classes
from rest_framework.decorators import api_view  
from .models import Rating, Professor, Module, ModuleInstance  
from django.db.models import Avg  
from django.http import JsonResponse 
from rest_framework.views import APIView 
from rest_framework.response import Response 
from django.shortcuts import get_object_or_404 
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.urls import path
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from rest_framework.authtoken.models import Token

import json

#class-based view to get the average rating of a professor in a specific module
class professor_module_rating_view(APIView):
    def get(self, request, professor_id, module_id):
        try:
            print(f"Fetching Professor with ID: {professor_id}")
            #fetch professor by ID
            professor = get_object_or_404(Professor, professor_id=professor_id)  
            print(f"Found Professor: {professor}")

            print(f"Fetching Module with Code: {module_id}")
            #fetch module by code
            module = get_object_or_404(Module, code=module_id)  
            print(f"Found Module: {module}")

            #fetch all module instances associated with the given professor and module
            module_instances = ModuleInstance.objects.filter(module=module, professors=professor)
            print(f"Module Instances: {module_instances}")

            #ff no module instances exist for the professor, return an error response
            if not module_instances.exists():
                print("No module instance found for this professor.")
                return Response({"error": "No module instance found for this professor."}, status=404)

            #fetch ratings related to the professor and module
            ratings = Rating.objects.filter(professor=professor, module_instance__module=module)
            print(f"Ratings Found: {ratings}")

            #calculate the average rating
            avg_rating = ratings.aggregate(Avg('rating')).get('rating__avg', None)
            print(f"Average Rating: {avg_rating}")

            #if there are no ratings, return a message 
            if avg_rating is None:
                return Response({"average_rating": "No ratings yet"}) 

            #return the rounded average rating
            return Response({"average_rating": round(avg_rating)}) 

        except Exception as e:
            print(f"🚨 ERROR: {str(e)}")
            #return an error response if something goes wrong
            return Response({"error": str(e)}, status=500)  
        
#function-based view to fetch all professor ratings
@api_view(["GET"])
def professor_ratings(request):
    #retrieve average ratings per professor
    ratings = Rating.objects.values("professor").annotate(average_rating=Avg("rating"))
    
    #convert ratings into a structured JSON response
    data = [
        {
            "professor_id": professor["professor"],
            "name": Professor.objects.get(professor_id=professor["professor"]).name,  # Get professor's name
            "rating": round(professor["average_rating"], 1) if professor["average_rating"] else "No ratings yet"
        }
        for professor in ratings
    ]

    #return the professor rating data
    return JsonResponse(data, safe=False)  

#function-based view to allow users to rate a professor
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def rate_professor(request):
    try:
        data = json.loads(request.body)
        print("📌 Received Data:", data)  # Print incoming data

        user_id = request.user.id  
        professor_id = data.get("professor_id")
        module_instance_id = data.get("module_instance")
        rating_value = data.get("rating")

        print(f"🔍 Looking for Professor: {professor_id}")
        professor = Professor.objects.get(professor_id=professor_id)
        print(f"✅ Found Professor: {professor}")

        print(f"🔍 Looking for ModuleInstance: {module_instance_id}")
        module_instance = ModuleInstance.objects.get(pk=module_instance_id)
        print(f"✅ Found ModuleInstance: {module_instance}")

        rating, created = Rating.objects.update_or_create(
            user=request.user,
            professor=professor,
            module_instance=module_instance,
            defaults={"rating": rating_value}
        )
        
        print(f"✅ Rating submitted successfully: {rating.rating}")
        return JsonResponse({"message": "Rating submitted successfully", "rating_id": rating.id}, status=201)

    except Professor.DoesNotExist:
        print("❌ ERROR: Professor Not Found")
        return JsonResponse({"error": "Professor not found"}, status=404)

    except ModuleInstance.DoesNotExist:
        print("❌ ERROR: ModuleInstance Not Found")
        return JsonResponse({"error": "Module instance not found"}, status=404)

    except Exception as e:
        print(f"🚨 ERROR: {str(e)}")
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt  
def register_view(request):
    #ensure only POST requests are processed
    if request.method == "POST":  
        try:
            data = json.loads(request.body)

            #extract username, email, and password from the request
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")

            #check if the username is already taken
            if User.objects.filter(username=username).exists():
                return JsonResponse({"error": "Username already exists"}, status=400)

            #create a new user in the database
            user = User.objects.create_user(username=username, email=email, password=password)

            #return a success response
            return JsonResponse({"message": "User registered successfully"}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    #if the request is not a POST request, return an error
    return JsonResponse({"error": "Invalid request method"}, status=405)

#COMMENT
@csrf_exempt  # Remove this in production
def login_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Read JSON request
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return JsonResponse({"error": "Username and password required"}, status=400)

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # 🔥 Generate or get existing token for the user
                token, created = Token.objects.get_or_create(user=user)
                
                return JsonResponse({"message": "Login successful!", "token": token.key}, status=200)
            else:
                return JsonResponse({"error": "Invalid credentials"}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Only POST requests allowed"}, status=405)

#COMMENT
@csrf_exempt
def logout_view(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "No active session found"}, status=400)

        logout(request)
        return JsonResponse({"message": "Logout successful!"}, status=200)

    return JsonResponse({"error": "Only POST requests allowed"}, status=405)

#COMMENT
@api_view(["GET"])
def list_modules(request):
    modules = ModuleInstance.objects.select_related("module").prefetch_related("professors").all()

    data = [
        {
            "module_code": instance.module.code,
            "module_name": instance.module.name,
            "year": instance.year,
            "semester": instance.semester,
            "professors": [prof.name for prof in instance.professors.all()]
        }
        for instance in modules
    ]

    return JsonResponse(data, safe=False)