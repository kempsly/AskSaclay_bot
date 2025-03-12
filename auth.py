import streamlit as st
import firebase_admin
from firebase_admin import auth, firestore
from firebase_config import db
from pyrebase import pyrebase
from dotenv import load_dotenv
import os
import logging

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()

# Firebase configuration (loaded from .env)
firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
    "databaseURL": "",  # Leave empty if not using Realtime Database
}

# Initialize Pyrebase for email/password authentication
pb = pyrebase.initialize_app(firebase_config)
auth_pyrebase = pb.auth()

# Sign up a new user
def sign_up(email, password):
    try:
        # Create user in Firebase Authentication
        user = auth.create_user(email=email, password=password)
        st.success("Account created successfully! Please log in.")

        # Save user data to Firestore (including an empty chat history)
        user_data = {
            "email": email,
            "created_at": firestore.SERVER_TIMESTAMP,
            "chat_history": []  # Initialize empty chat history
        }
        db.collection("users").document(user.uid).set(user_data)
        logging.debug(f"User {user.uid} created and data saved to Firestore.")
        return user.uid
    except Exception as e:
        logging.error(f"Error creating account: {e}")
        st.error(f"Error creating account: {e}")
        return None

# Log in an existing user
def sign_in(email, password):
    try:
        # Authenticate user using Pyrebase
        user = auth_pyrebase.sign_in_with_email_and_password(email, password)
        st.session_state.user = user  # Store user in session state

        # Fetch user's chat history from Firestore
        user_ref = db.collection("users").document(user["localId"])
        user_doc = user_ref.get()

        if user_doc.exists:
            # Load existing chat history
            st.session_state.chat_history = user_doc.to_dict().get("chat_history", [])
            logging.debug(f"Chat history loaded for user {user['localId']}.")
        else:
            # Create a new document for the user if it doesn't exist
            user_ref.set({
                "email": email,
                "created_at": firestore.SERVER_TIMESTAMP,
                "chat_history": []  # Initialize empty chat history
            })
            st.session_state.chat_history = []
            logging.debug(f"New user document created for {user['localId']}.")

        st.success("Logged in successfully!")
        return user
    except Exception as e:
        logging.error(f"Error logging in: {e}")
        st.error(f"Error logging in: {e}")
        return None

# Log out the current user
def logout():
    if "user" in st.session_state:
        # Save chat history to Firestore before logging out
        user_id = st.session_state.user["localId"]
        try:
            db.collection("users").document(user_id).update({
                "chat_history": st.session_state.get("chat_history", [])
            })
            logging.debug(f"Chat history saved for user {user_id}.")
        except Exception as e:
            logging.error(f"Error saving chat history: {e}")
            st.error(f"Error saving chat history: {e}")

        # Clear session state
        del st.session_state.user
        if "chat_history" in st.session_state:
            del st.session_state.chat_history
        st.success("Logged out successfully!")









############################################
#_________________________________________________
#_________________________________________________
#_________________________________________________
#_________________________________________________
#_________________________________________________
#_________________________________________________
#_________________________________________________
# import streamlit as st
# import firebase_admin
# from firebase_admin import auth, firestore
# from firebase_config import db
# from pyrebase import pyrebase
# from dotenv import load_dotenv
# import os

# # Load environment variables from .env file
# load_dotenv()

# # Firebase configuration (loaded from .env)
# firebase_config = {
#     "apiKey": os.getenv("FIREBASE_API_KEY"),
#     "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
#     "projectId": os.getenv("FIREBASE_PROJECT_ID"),
#     "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
#     "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
#     "appId": os.getenv("FIREBASE_APP_ID"),
#     "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
#     "databaseURL": "",  # Leave empty if not using Realtime Database
# }

# # Initialize Pyrebase for email/password authentication
# pb = pyrebase.initialize_app(firebase_config)
# auth_pyrebase = pb.auth()

# # Sign up a new user
# def sign_up(email, password):
#     try:
#         user = auth.create_user(email=email, password=password)
#         st.success("Account created successfully! Please log in.")
#         # Save user data to Firestore (including an empty chat history)
#         user_data = {
#             "email": email,
#             "created_at": firestore.SERVER_TIMESTAMP,
#             "chat_history": []  # Initialize empty chat history
#         }
#         db.collection("users").document(user.uid).set(user_data)
#         return user.uid
#     except Exception as e:
#         st.error(f"Error creating account: {e}")
#         return None

# # # Log in an existing user
# # def sign_in(email, password):
# #     try:
# #         # Authenticate user using Pyrebase
# #         user = auth_pyrebase.sign_in_with_email_and_password(email, password)
# #         st.session_state.user = user  # Store user in session state

# #         # Fetch user's chat history from Firestore
# #         user_doc = db.collection("users").document(user["localId"]).get()
# #         if user_doc.exists:
# #             st.session_state.chat_history = user_doc.to_dict().get("chat_history", [])
# #         else:
# #             st.session_state.chat_history = []

# #         st.success("Logged in successfully!")
# #         return user
# #     except Exception as e:
# #         st.error(f"Error logging in: {e}")
# #         return None


# def sign_in(email, password):
#     try:
#         # Authenticate user using Pyrebase
#         user = auth_pyrebase.sign_in_with_email_and_password(email, password)
#         st.session_state.user = user  # Store user in session state

#         # Fetch user's chat history from Firestore
#         user_ref = db.collection("users").document(user["localId"])
#         user_doc = user_ref.get()

#         if user_doc.exists:
#             st.session_state.chat_history = user_doc.to_dict().get("chat_history", [])
#             logging.debug(f"Chat history loaded for user {user['localId']}.")
#         else:
#             # Create a new document for the user if it doesn't exist
#             user_ref.set({
#                 "email": email,
#                 "created_at": firestore.SERVER_TIMESTAMP,
#                 "chat_history": []  # Initialize empty chat history
#             })
#             st.session_state.chat_history = []
#             logging.debug(f"New user document created for {user['localId']}.")

#         st.success("Logged in successfully!")
#         return user
#     except Exception as e:
#         logging.error(f"Error logging in: {e}")
#         st.error(f"Error logging in: {e}")
#         return None

# # Log out the current user
# def logout():
#     if "user" in st.session_state:
#         # Save chat history to Firestore before logging out
#         user_id = st.session_state.user["localId"]
#         db.collection("users").document(user_id).update({
#             "chat_history": st.session_state.get("chat_history", [])
#         })
#         del st.session_state.user
#         if "chat_history" in st.session_state:
#             del st.session_state.chat_history
#         st.success("Logged out successfully!")

############################################
#_________________________________________________
#_________________________________________________
#_________________________________________________
#_________________________________________________
#_________________________________________________
#_________________________________________________
#_________________________________________________
# WITHOUT THE FUNCTIONALISTIES TO SAVE THE CHAT HISTORY

# import streamlit as st
# import firebase_admin
# from firebase_admin import auth, firestore
# from firebase_config import db
# # from pyrebase import pyrebase
# from dotenv import load_dotenv
# import os
# from pyrebase import pyrebase

# # Load environment variables from .env file
# load_dotenv()

# # Firebase configuration (loaded from .env)
# firebase_config = {
#     "apiKey": os.getenv("FIREBASE_API_KEY"),
#     "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
#     "projectId": os.getenv("FIREBASE_PROJECT_ID"),
#     "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
#     "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
#     "appId": os.getenv("FIREBASE_APP_ID"),
#     "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
#     "databaseURL": "",  # Leave empty if not using Realtime Database
# }

# # Initialize Pyrebase for email/password authentication
# pb = pyrebase.initialize_app(firebase_config)
# auth_pyrebase = pb.auth()

# # Sign up a new user
# def sign_up(email, password):
#     try:
#         user = auth.create_user(email=email, password=password)
#         st.success("Account created successfully! Please log in.")
#         # Save user data to Firestore (optional)
#         user_data = {"email": email, "created_at": firestore.SERVER_TIMESTAMP}
#         db.collection("users").document(user.uid).set(user_data)
#         return user.uid
#     except Exception as e:
#         st.error(f"Error creating account: {e}")
#         return None

# # Log in an existing user
# def sign_in(email, password):
#     try:
#         # Authenticate user using Pyrebase
#         user = auth_pyrebase.sign_in_with_email_and_password(email, password)
#         st.session_state.user = user  # Store user in session state
#         st.success("Logged in successfully!")
#         return user
#     except Exception as e:
#         st.error(f"Error logging in: {e}")
#         return None

# # Log out the current user
# def logout():
#     if "user" in st.session_state:
#         del st.session_state.user
#         st.success("Logged out successfully!")