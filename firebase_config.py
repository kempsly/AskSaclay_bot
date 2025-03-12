
############################################################################################
############################################################################################
############################################################################################
#################################################### WITH DEEP###############################
import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
from dotenv import load_dotenv

load_dotenv()


def initialize_firebase():
    # Load Firebase credentials from environment variable
    firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
    if firebase_credentials_json:
        credentials_dict = json.loads(firebase_credentials_json)
        cred = credentials.Certificate(credentials_dict)
    else:
        raise ValueError("FIREBASE_CREDENTIALS_JSON environment variable is not set.")
    firebase_admin.initialize_app(cred)

initialize_firebase()
db = firestore.client()

#------------------------------------------
# import firebase_admin
# from firebase_admin import credentials, auth, firestore

# # Initialize Firebase
# def initialize_firebase():
#     if not firebase_admin._apps:
#         cred = credentials.Certificate("serviceAccountKey.json")
#         firebase_admin.initialize_app(cred)

# # Export Firebase services
# initialize_firebase()
# db = firestore.client()

#-------------------------------------------
# import os
# import json
# import firebase_admin
# from firebase_admin import credentials, firestore

# # Initialize Firebase with credentials from environment variable
# def initialize_firebase():
#     if not firebase_admin._apps:
#         # Load Firebase credentials from environment variable
#         firebase_credentials_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
        
#         if firebase_credentials_json:
#             # Parse the JSON credentials
#             credentials_dict = json.loads(firebase_credentials_json)
            
#             # Initialize Firebase Admin SDK using the credentials
#             cred = credentials.Certificate(credentials_dict)
#             firebase_admin.initialize_app(cred)
#         else:
#             raise ValueError("FIREBASE_CREDENTIALS_JSON environment variable is not set.")

# # Export Firebase services
# initialize_firebase()
# db = firestore.client()

