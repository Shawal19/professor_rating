import requests
import getpass
import json

#API Endpoints
REGISTER_URL = "http://127.0.0.1:8000/register/"  
LOGIN_URL = "http://127.0.0.1:8000/login/"  
LOGOUT_URL = "http://127.0.0.1:8000/logout/"
LIST_URL = "http://127.0.0.1:8000/api/modules/"  
VIEW_URL = "http://127.0.0.1:8000/api/professor-ratings/"
AVERAGE_URL = "http://127.0.0.1:8000/api/professors/{professor_id}/modules/{module_code}/rating/"
RATE_URL = "http://127.0.0.1:8000/api/ratings/"

def register():
    print("User Registration:")

    #prompt user for input
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = input("Enter password: ")

    #construct the request data as a JSON object
    data = {"username": username, "email": email, "password": password}

    try:
        response = requests.post(REGISTER_URL, json=data)

        if response.status_code == 201:
            print("Registration successful!")
        else:
            print(f"Registration failed: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")

#COMMENT
TOKEN = None  # Store the token globally

def login():
    global TOKEN
    print("🔑 User Login:")
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")  # Hide password input

    headers = {"Content-Type": "application/json"}
    data = json.dumps({"username": username, "password": password})  

    response = requests.post(LOGIN_URL, headers=headers, data=data)
    
    if response.status_code == 200:
        json_response = response.json()
        TOKEN = json_response.get("token")

        if TOKEN:
            print("✅ Login successful! Token received.")
        else:
            print("⚠️ Login successful, but no token received.")
    else:
        print(f"❌ Login failed: {response.text}")

#COMMENT
def logout():
    print("Logging out...")

    try:
        response = requests.post(LOGOUT_URL)

        if response.status_code == 200:
            print("Logout successful!")
        else:
            print(f"Logout failed: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")

#COMMENT
def list():
    print("\nRetrieving Module List...\n")

    try:
        response = requests.get(LIST_URL)

        if response.status_code == 200:
            modules = response.json()
            if not modules:
                print("No modules found.")
                return

            #print table headers
            print(f"{'Code':<5} {'Name':<30} {'Year':<6} {'Semester':<8} {'Taught by'}")
            print("-" * 80)

            for module in modules:
                professors = ", ".join(module["professors"]) if module["professors"] else "None"
                print(f"{module['module_code']:<5} {module['module_name']:<30} {module['year']:<6} {module['semester']:<8} {professors}")
                print("-" * 80)

        else:
            print(f"Failed to retrieve modules: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")

#COMMENT
def view_ratings():
    try:
        response = requests.get(VIEW_URL)

        if response.status_code == 200:
            ratings = response.json()
            
            if not ratings:
                print("No ratings available.")
                return
            
            print("\nProfessor Ratings:")
            for professor in ratings:
                stars = "*" * int(professor["rating"]) if professor["rating"] != "No ratings yet" else "No ratings yet"
                print(f"The rating of {professor['name']} ({professor['professor_id']}) is {stars}")

        else:
            print(f"Failed to fetch ratings: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")

#COMMENT
def average_rating():
    professor_id = input("Enter professor ID: ").strip()
    module_code = input("Enter module code: ").strip()

    try:
        response = requests.get(AVERAGE_URL)
        data = response.json()

        if response.status_code == 200:
            avg_rating = data.get("average_rating")

            # Check if avg_rating is an integer, otherwise print the message
            if isinstance(avg_rating, int):
                print(f"The rating of Professor {professor_id} in module {module_code} is {'*' * avg_rating}")
            else:
                print(f"The rating of Professor {professor_id} in module {module_code} is {avg_rating}")

        else:
            print(f"Failed to fetch rating: {data}")

    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")

#COMMENT
def rate_professor():
    """ Example function that requires authentication """
    global TOKEN
    if not TOKEN:
        print("❌ You must log in first!")
        return
    
    print("📌 Rate a Professor:")
    professor_id = input("Enter professor ID: ")
    module_code = input("Enter module code: ")
    year = input("Enter teaching year: ")
    semester = input("Enter semester: ")
    rating = input("Enter rating (1-5): ")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {TOKEN}"  # 🔥 Send the token
    }

    data = json.dumps({
        "professor_id": professor_id,
        "module_code": module_code,
        "year": year,
        "semester": semester,
        "rating": rating
    })

    response = requests.post(RATE_URL, headers=headers, data=data)

    if response.status_code == 201:
        print("✅ Rating submitted successfully!")
    else:
        print(f"❌ Rating submission failed: {response.text}")

def main():
    while True:
        #get user input and normalize it
        command = input("> ").strip().lower()

         #call the register function
        if command == "register":
            register()
        
        #call the login function
        elif command == "login":
            login()
        
        #call the logout function
        elif command == "logout":
            logout()

        #combine "list" command with option 1
        elif command == "list" or command == "1":  
            list()

        #call the function to fetch and display ratings
        elif command == "view":
            view_ratings()  
        
        elif command == "average":
            average_rating()
        
        elif command == "rate":
            rate_professor()

        #exit the program
        elif command in ["exit", "quit"]:
            print("Goodbye!")
            break

        else:
            print("Unknown command. Try 'register', 'login', 'logout', 'list', 'view', 'average', or 'exit'.")

if __name__ == "__main__":
    main()

