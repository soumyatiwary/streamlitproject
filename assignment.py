import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px

# Global Variables
json_file = 'users.json'

# Function to check if JSON exists, otherwise create it as an empty dictionary
def check_json():
    if not os.path.exists(json_file):
        with open(json_file, 'w') as f:
            json.dump({}, f)  # Initialize as an empty dictionary

# Function to load users from JSON
def load_users():
    with open(json_file, 'r') as f:
        data = json.load(f)
        if isinstance(data, dict):
            return data
        else:
            return {}  # Ensure it returns a dictionary

# Function to save users to JSON
def save_users(users):
    with open(json_file, 'w') as f:
        json.dump(users, f)

# Function to create a folder for each user
def create_user_folder(username):
    folder_path = os.path.join(os.getcwd(), f'{username}_marks')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

# Page 1: Signup/Login Page
def login_signup_page():
    st.title('Login/Signup Page')

    # Radio button on the sidebar
    option = st.sidebar.radio('Choose Option', ['Login', 'Sign Up'])

    if option == 'Sign Up':
        st.subheader('Create a new account')
        name = st.text_input('Name')
        phone = st.text_input('Phone')
        dob = st.date_input('Date of Birth')
        email = st.text_input('Email')
        password = st.text_input('Password', type='password')

        if st.button('Sign Up'):
            users = load_users()
            if email in users:
                st.error('User already exists with this email.')
            else:
                users[email] = {
                    'name': name,
                    'phone': phone,
                    'dob': str(dob),
                    'password': password
                }
                save_users(users)
                create_user_folder(email)
                st.success('Signup successful! Please login now.')

    elif option == 'Login':
        st.subheader('Login to your account')
        email = st.text_input('Email')
        password = st.text_input('Password', type='password')

        if st.button('Login'):
            users = load_users()
            if email in users and users[email]['password'] == password:
                st.session_state['email'] = email
                st.session_state['name'] = users[email]['name']
                st.session_state['logged_in'] = True
                st.experimental_rerun()  # Rerun the app to switch to the main interface
            else:
                st.error('Invalid email or password.')

# Page 2: Marks Entry Page
def marks_entry_page():
    st.title(f'Welcome {st.session_state["name"]}')

    subjects = ['Maths', 'Physics', 'Chemistry', 'English', 'Hindi']
    marks = {}

    for subject in subjects:
        marks[subject] = st.slider(f'Choose your marks for {subject}', 0, 100)

    if st.button('Submit Marks'):
        user_folder = create_user_folder(st.session_state['email'])
        marks_df = pd.DataFrame([marks])
        csv_path = os.path.join(user_folder, f'{st.session_state["email"]}_marks.csv')
        marks_df.to_csv(csv_path, index=False)
        st.success('Marks saved successfully!')

# Page 3: Graphical Reports Page
def report_page():
    st.title('Your Reports are Ready!')

    user_folder = create_user_folder(st.session_state['email'])
    csv_path = os.path.join(user_folder, f'{st.session_state["email"]}_marks.csv')

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)

        # 1. Average Marks Bar Graph
        avg_marks = df.mean(axis=1).iloc[0]
        st.write(f"Average Marks: {avg_marks}")
        st.bar_chart(df.mean())

        # 2. Marks per Subject - Line Graph
        st.write('Marks per subject (Line Graph)')
        fig1 = px.line(df.T, title='Marks Per Subject - Line Graph')
        st.plotly_chart(fig1)

        # 3. Marks per Subject - Pie Chart
        st.write('Marks per subject (Pie Chart)')
        fig2 = px.pie(df.T, names=df.columns, values=df.iloc[0], title='Marks Per Subject - Pie Chart')
        st.plotly_chart(fig2)

    else:
        st.error('No marks found! Please submit your marks first.')

# Page 4: Logout Page
def logout_page():
    st.title('Logout')

    if st.button('Logout'):
        st.session_state['logged_in'] = False
        st.session_state['email'] = None
        st.session_state['name'] = None
        st.experimental_rerun()  # Rerun the app to go back to the login/signup page

# Main function to manage navigation
def main():
    check_json()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login_signup_page()
    else:
        pages = {
            'Marks Entry': marks_entry_page,
            'Reports': report_page,
            'Logout': logout_page
        }

        page = st.sidebar.selectbox('Navigation', list(pages.keys()))
        pages[page]()

if __name__ == '__main__':
    main()
