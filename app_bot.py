# # import streamlit as st
# # from auth import sign_up, login
# # from chatbot import chatbot_ui

# # st.title("🔥 Chatbot Authentication")

# # if "authenticated" not in st.session_state:
# #     st.session_state.authenticated = False

# # if not st.session_state.authenticated:
# #     option = st.radio("Choose an option", ["Sign Up", "Login"])

# #     email = st.text_input("Email")
# #     password = st.text_input("Password", type="password")

# #     if option == "Sign Up":
# #         if st.button("Sign Up"):
# #             user = sign_up(email, password)
# #             if isinstance(user, dict):
# #                 st.success("Sign-up successful! Please log in.")
# #             else:
# #                 st.error(user)

# #     else:
# #         if st.button("Login"):
# #             user = login(email, password)
# #             if isinstance(user, dict):
# #                 st.session_state.authenticated = True
# #                 st.session_state.email = email
# #                 st.experimental_rerun()
# #             else:
# #                 st.error("Invalid credentials.")

# # if st.session_state.authenticated:
# #     chatbot_ui()

# import streamlit as st
# from auth import sign_up, sign_in
# from chatbot import chatbot_response

# st.title("🗣️ Chatbot with Firebase Authentication")

# # Authentication state
# if "user" not in st.session_state:
#     st.session_state["user"] = None

# # Login / Signup
# tab1, tab2 = st.tabs(["Login", "Signup"])

# with tab1:
#     st.subheader("🔑 Login")
#     email = st.text_input("Email")
#     password = st.text_input("Password", type="password")
#     if st.button("Sign In"):
#         user_data = sign_in(email, password)
#         if user_data:
#             st.session_state["user"] = user_data
#             st.success("✅ Logged in successfully!")
#             st.rerun()
#         else:
#             st.error("❌ Invalid credentials!")

# with tab2:
#     st.subheader("🆕 Signup")
#     new_email = st.text_input("New Email")
#     new_password = st.text_input("New Password", type="password")
#     if st.button("Sign Up"):
#         user_id = sign_up(new_email, new_password)
#         if user_id:
#             st.success("✅ Account created! Please login.")
#         else:
#             st.error("❌ Signup failed!")

# # Chatbot UI (only if logged in)
# if st.session_state["user"]:
#     st.subheader("💬 Chatbot")
#     user_input = st.text_input("You: ")
#     if st.button("Send"):
#         response = chatbot_response(user_input)
#         st.write(f"🤖 Chatbot: {response}")


############################################################################################
############################################################################################
############################################################################################
#################################################### WITH DEEP###############################


# import streamlit as st
# from auth import sign_up, sign_in, logout
# from bot import chatbot_ui

# # Main app logic
# st.title("🗣️ Chatbot with Firebase Authentication")

# # Authentication state
# if "user" not in st.session_state:
#     st.session_state.user = None

# # Login / Signup
# tab1, tab2 = st.tabs(["Login", "Signup"])

# with tab1:
#     st.subheader("🔑 Login")
#     email = st.text_input("Email")
#     password = st.text_input("Password", type="password")
#     if st.button("Sign In"):
#         user = sign_in(email, password)
#         if user:
#             st.session_state.user = user
#             st.rerun()

# with tab2:
#     st.subheader("🆕 Signup")
#     new_email = st.text_input("New Email")
#     new_password = st.text_input("New Password", type="password")
#     if st.button("Sign Up"):
#         user_id = sign_up(new_email, new_password)
#         if user_id:
#             st.success("Account created! Please log in.")

# # Logout button
# if st.session_state.user:
#     if st.button("Log Out"):
#         logout()
#         st.session_state.user = None
#         st.rerun()

# # Chatbot UI (only if logged in)
# if st.session_state.user:
#     chatbot_ui()


####################
###############################
# import streamlit as st
# from auth import sign_up, sign_in, logout
# from bot import chatbot_ui

# # Main app logic
# st.title("🗣️ Chatbot with Firebase Authentication")

# # Authentication state
# if "user" not in st.session_state:
#     st.session_state.user = None

# # Sidebar for logout or user profile
# if st.session_state.user:
#     st.sidebar.markdown("### User Profile")
#     user_email = st.session_state.user["email"]
    
#     # Display user profile with the first letter of the email
#     profile_letter = user_email[0].upper()  # First letter of the email
#     st.sidebar.markdown(f"**{profile_letter}**")  # Display the letter as a profile icon
    
#     # Logout button
#     if st.sidebar.button("Log Out"):
#         logout()
#         st.session_state.user = None
#         st.rerun()

# # If the user is logged in, show the chatbot UI
# if st.session_state.user:
#     chatbot_ui()
# else:
#     # If the user is not logged in, show the authentication page
#     tab1, tab2 = st.tabs(["Login", "Signup"])

#     with tab1:
#         st.subheader("🔑 Login")
#         email = st.text_input("Email")
#         password = st.text_input("Password", type="password")
#         if st.button("Sign In"):
#             user = sign_in(email, password)
#             if user:
#                 st.session_state.user = user
#                 st.rerun()

#     with tab2:
#         st.subheader("🆕 Signup")
#         new_email = st.text_input("New Email")
#         new_password = st.text_input("New Password", type="password")
#         if st.button("Sign Up"):
#             user_id = sign_up(new_email, new_password)
#             if user_id:
#                 st.success("Account created! Please log in.")

######
### With profile in circle shape
# import streamlit as st
# from auth import sign_up, sign_in, logout
# from bot import chatbot_ui

# # Main app logic
# st.title("🗣️ Chatbot with Firebase Authentication")

# # Authentication state
# if "user" not in st.session_state:
#     st.session_state.user = None
# if "show_logout" not in st.session_state:
#     st.session_state.show_logout = False  # Control visibility of the logout button

# # Sidebar for user profile and logout
# with st.sidebar:
#     if st.session_state.user:
#         user_email = st.session_state.user["email"]
#         profile_letter = user_email[0].upper()  # First letter of the email

#         # Custom CSS to style the profile button as a circle
#         st.markdown(
#             """
#             <style>
#             .profile-button {
#                 display: inline-block;
#                 width: 40px;
#                 height: 40px;
#                 border-radius: 50%;
#                 background-color: #4CAF50;
#                 color: white;
#                 text-align: center;
#                 line-height: 40px;
#                 font-size: 18px;
#                 font-weight: bold;
#                 cursor: pointer;
#                 border: none;
#                 outline: none;
#                 margin-bottom: 10px;  # Space between profile button and logout button
#             }
#             .profile-button:hover {
#                 background-color: #45a049;
#             }
#             </style>
#             """,
#             unsafe_allow_html=True,
#         )

#         # Display the circular profile button using Streamlit's button
#         if st.button(profile_letter, key="profile_button"):
#             # Toggle the logout button visibility
#             st.session_state.show_logout = not st.session_state.show_logout

#         # Display the logout button if toggled
#         if st.session_state.show_logout:
#             if st.button("Log Out", key="logout_button"):
#                 logout()
#                 st.session_state.user = None
#                 st.session_state.show_logout = False
#                 st.rerun()

# # If the user is logged in, show the chatbot UI
# if st.session_state.user:
#     chatbot_ui()
# else:
#     # If the user is not logged in, show the authentication page
#     tab1, tab2 = st.tabs(["Login", "Signup"])

#     with tab1:
#         st.subheader("🔑 Login")
#         email = st.text_input("Email")
#         password = st.text_input("Password", type="password")
#         if st.button("Sign In"):
#             user = sign_in(email, password)
#             if user:
#                 st.session_state.user = user
#                 st.rerun()

#     with tab2:
#         st.subheader("🆕 Signup")
#         new_email = st.text_input("New Email")
#         new_password = st.text_input("New Password", type="password")
#         if st.button("Sign Up"):
#             user_id = sign_up(new_email, new_password)
#             if user_id:
#                 st.success("Account created! Please log in.")



################
# import streamlit as st
# from auth import sign_up, sign_in, logout
# from bot import chatbot_ui

# # Main app logic
# st.title("🗣️ Chatbot with Firebase Authentication")

# # Authentication state
# if "user" not in st.session_state:
#     st.session_state.user = None
# if "show_logout" not in st.session_state:
#     st.session_state.show_logout = False  # Control visibility of the logout button

# # Sidebar for user profile and logout
# with st.sidebar:
#     if st.session_state.user:
#         user_email = st.session_state.user["email"]
#         profile_letter = user_email[0].upper()  # First letter of the email

#         # Custom CSS to style the profile button as a circle
#         st.markdown(
#             """
#             <style>
#             .profile-button {
#                 display: inline-block;
#                 width: 40px;
#                 height: 40px;
#                 border-radius: 50%;
#                 background-color: #2196F3;  # Changed to blue
#                 color: white;
#                 text-align: center;
#                 line-height: 40px;
#                 font-size: 18px;
#                 font-weight: bold;
#                 cursor: pointer;
#                 border: none;
#                 outline: none;
#                 margin-bottom: 10px;  # Space between profile button and logout button
#             }
#             .profile-button:hover {
#                 background-color: #1976D2;  # Darker blue on hover
#             }
#             </style>
#             """,
#             unsafe_allow_html=True,
#         )

#         # Display the circular profile button using Streamlit's button
#         if st.button(profile_letter, key="profile_button"):
#             # Toggle the logout button visibility
#             st.session_state.show_logout = not st.session_state.show_logout

#         # Display the logout button if toggled
#         if st.session_state.show_logout:
#             if st.button("Log Out", key="logout_button"):
#                 logout()
#                 st.session_state.user = None
#                 st.session_state.show_logout = False
#                 st.rerun()

# # If the user is logged in, show the chatbot UI
# if st.session_state.user:
#     chatbot_ui()
# else:
#     # If the user is not logged in, show the authentication page
#     tab1, tab2 = st.tabs(["Login", "Signup"])

#     with tab1:
#         st.subheader("🔑 Login")
#         email = st.text_input("Email")
#         password = st.text_input("Password", type="password")
#         if st.button("Sign In"):
#             user = sign_in(email, password)
#             if user:
#                 st.session_state.user = user
#                 st.rerun()

#     with tab2:
#         st.subheader("🆕 Signup")
#         new_email = st.text_input("New Email")
#         new_password = st.text_input("New Password", type="password")
#         if st.button("Sign Up"):
#             user_id = sign_up(new_email, new_password)
#             if user_id:
#                 st.success("Account created! Please log in.")



##############################################
#########################################################
######################################################################################
import streamlit as st
from auth import sign_up, sign_in, logout
from bot import chatbot_ui

# Main app logic
st.title("🤖 AskSaclayAI: Your AI Assistant for University Paris-Saclay")

# Authentication state
if "user" not in st.session_state:
    st.session_state.user = None
if "show_logout" not in st.session_state:
    st.session_state.show_logout = False  # Control visibility of the logout button

# Sidebar for user profile and logout
with st.sidebar:
    if st.session_state.user:
        user_email = st.session_state.user["email"]
        profile_letter = user_email[0].upper()  # First letter of the email

        # Custom CSS to style the profile button as a circle
        st.markdown(
            """
            <style>
            .profile-button {
                display: inline-block;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background-color: #2196F3;  # Blue color
                color: white;
                text-align: center;
                line-height: 40px;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                border: none;
                outline: none;
                margin-bottom: 10px;  # Space between profile button and logout button
            }
            .profile-button:hover {
                background-color: #1976D2;  # Darker blue on hover
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Display the circular profile button using Streamlit's button
        if st.button(profile_letter, key="profile_button"):
            # Toggle the logout button visibility
            st.session_state.show_logout = not st.session_state.show_logout

        # Display the logout button if toggled
        if st.session_state.show_logout:
            if st.button("Log Out", key="logout_button"):
                logout()
                st.session_state.user = None
                st.session_state.show_logout = False
                st.rerun()

# If the user is logged in, show the chatbot UI
if st.session_state.user:
    chatbot_ui()
else:
    # If the user is not logged in, show the authentication page
    st.markdown(
        """
        <div style="text-align: center;">
            <h2>Welcome to AskSaclayAI</h2>
            <p>Your AI-powered assistant for Université Paris-Saclay.</p>
            <p>Sign up or log in to get started!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        st.subheader("🔑 Login to AskSaclayAI")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Sign In"):
            user = sign_in(email, password)
            if user:
                st.session_state.user = user
                st.rerun()

    with tab2:
        st.subheader("🆕 Create an Account")
        new_email = st.text_input("New Email")
        new_password = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            user_id = sign_up(new_email, new_password)
            if user_id:
                st.success("Account created! Please log in.")