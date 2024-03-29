# Importing the necessary libraries

######## Before running this code, please enter "pip install gspread" into your terminal so that all features run correctly. ########

######## Please restart the kernel! ########


from IPython.display import display, Image, clear_output, HTML, Audio
from jupyter_ui_poll import ui_events
import ipywidgets as widgets
import time
import random
import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json 
import warnings
import gspread 

# Function to register the text input event
def register_text_input_event(text_input):
    """
    Registers the text input event.
    
    Parameters:
    text_input (Widget): The text input widget.
    """
    event_info['type'] = "text_entry"
    event_info['description'] = text_input.value
    event_info['time'] = time.time()
    return


# Function to create a text input widget to improve user interface
def text_input(prompt=None):
    """
    Creates a text input widget.
    
    Parameters:
    prompt (str): The prompt to display for the text input widget.
    
    Returns:
    str: The text entered by the user.
    """
    text_widget = widgets.Text(description=prompt, style={'description_width': 'initial'})
    text_widget.on_submit(register_text_input_event)
    box_layout = widgets.Layout(display='flex', justify_content='center', align_items='center')
    box = widgets.Box([text_widget], layout=box_layout)
    display(box)
    event = wait_for_event()
    text_widget.disabled = True
    return text_widget

# Function to send data to Google Forms for collection

def send_to_google_form(data_dict, form_url):
    """
    Sends data to a Google Form.
    
    Parameters:
    data_dict (dict): A dictionary containing the data to be sent.
    form_url (str): The URL of the Google Form.
    
    Returns:
    bool: True if the data is successfully sent, False otherwise.
    """

    # Extracting form ID from the provided URL
    form_id = form_url[34:90]

    # URL template to view and post the form
    view_form_url = f'https://docs.google.com/forms/d/e/{form_id}/viewform'
    post_form_url = f'https://docs.google.com/forms/d/e/{form_id}/formResponse'

    # Fetching the form and extracting the required data for submission
    page = requests.get(view_form_url)
    content = BeautifulSoup(page.content, "html.parser").find('script', type='text/javascript')
    content = content.text[27:-1]
    result = json.loads(content)[1][1]

    # Mapping form fields to data dictionary keys
    form_dict = {}
    loaded_all = True
    for item in result:
        if item[1] not in data_dict:
            print(f"Form item {item[1]} not found. Data not uploaded.")
            loaded_all = False
            return False
        form_dict[f'entry.{item[4][0][0]}'] = data_dict[item[1]]
    # Sending the data to the Google Form
    post_result = requests.post(post_form_url, data=form_dict)
    return post_result.ok

# Function for waiting for an event
def wait_for_event(timeout=-1, interval=0.001, max_rate=20, allow_interupt=True):    
    start_wait = time.time()
    """
    Waits for an event to occur.
    
    Parameters:
    timeout (float): The timeout period in seconds. Default is -1 (no timeout).
    interval (float): The time interval between checks for events. Default is 0.001 seconds.
    max_rate (int): The maximum rate of events per second. Default is 20.
    allow_interupt (bool): Whether to allow interruption of the wait. Default is True.
    
    Returns:
    dict: Information about the event.
    """
    # This initialises and resets event information
    event_info['type'] = ""
    event_info['description'] = ""
    event_info['time'] = -1

    n_proc = int(max_rate*interval)+1
    
    with ui_events() as ui_poll:
        keep_looping = True
        while keep_looping==True:

            # Process UI events
            ui_poll(n_proc)

            # Ends the loop if the time spent looping is longer than the timeout period. Here, -1 can be set for no timeout.
            if (timeout != -1) and (time.time() > start_wait + timeout):
                keep_looping = False

            # When the event_info description changes, looping stops.
            if allow_interupt==True and event_info['description']!="":
                keep_looping = False

            time.sleep(interval)
    
    return event_info

# Function to register button clicking event
def register_btn_event(btn):
    event_info['type'] = "button click"
    event_info['description'] = btn.description
    event_info['time'] = time.time()

# Function to display widgets centered (to standardise aesthetics and reduce interruptions between reading the question and inputing the answer)
def display_centered(widget):
    # Setting layout for centered display
    box_layout = widgets.Layout(display='flex', justify_content='center', align_items='center')
    box = widgets.Box([widget], layout=box_layout)
    display(box)

# Callback function for submit button
def submit_button_callback():
    # This function is called when the submit button is clicked
    global gender, age
    # Extracting age and gender values from respective widgets
    age = age_dropdown.value
    gender = gender_radiobuttons.value
    # Call send_to_google_form here with correct data and URL
    clear_output(wait=False)

#Display a message for the user with a countdown feature before beginning test.
def timer(message):
    # Countdown from 5 to 0, displaying each number
    for i in range(5, 0, -1):
        clear_output(wait=True)
        formatted_message = message.format(i)
        style = "color: orchid; font-size: 100px; display: flex; justify-content: center; align-items: center;"
        display(HTML(f"<div style='{style}'><span>{formatted_message}</span></div>"))
        time.sleep(1)
    clear_output(wait=True)
timer_message = "Beginning the test in... {}"



# button used to input confirmation from user
confirm_btn = widgets.Button(description = "Confirm")

# Function to display the submit button
def submit_button(age_dropdown, gender_radiobuttons):
    confirm_btn = widgets.Button(description="Confirm and Begin")
    display_centered(confirm_btn)
    confirm_btn.on_click(register_btn_event)
    wait_for_event()
    submit_button_callback()
    clear_output(wait=False)

# This displays a confirm button for user interaction
def confirm_button():
    display_centered(confirm_btn)
    confirm_btn.on_click(register_btn_event)
    wait_for_event()
    clear_output(wait=False)
    return


# Initialize user_id as an empty string
user_id = ""

# Main function to get personal information
def personal_info(): 
    global user_id
    # Using HTML formatting to improve the text layout and make it more visually appealing
    personal_info_1 = 'Welcome to the Arithmetic test. This test will take approximately 3 minutes and the questions will progressively increase in difficulty.'
    personal_info_2 = 'Each part of the question will flash on your screen for 1.5 seconds after which you will be prompted to respond.'
    personal_info_3 = 'Your final score will be calculated based on the time taken to answer each question and the number of correct answers, so try to be quick and precise!'
    #creating HTML format for the introductory text
    style_personal_info = "color: cornflowerblue; font-size: 20px; display: flex; justify-content: center; align-items: center;"
    display(HTML(f"<div style='{style_personal_info}'><span>{personal_info_1}</span></div>"))
    display(HTML(f"<div style='{style_personal_info}'><span>{personal_info_2}</span></div>"))
    display(HTML(f"<div style='{style_personal_info}'><span>{personal_info_3}</span></div>"))
    time.sleep(3)
    
    #Creating HTML styles for the consent request text
    style_consent = "color: paleturquoise; font-size: 15px; display: flex; justify-content: center; align-items: center;"
    # Displaying instructions for creating an anonymous user ID
    display(HTML(f"""<span style='{style_consent}'>Please create an anonymous ID.<br /><br />
   To generate an anonymous 4-letter unique user identifier please enter:<br />
    - two letters based on the initials (first and last name) of a childhood friend<br /> 
    - two letters based on the initials (first and last name) of a favourite actor / actress<br />
   e.g. if your friend was called Charlie Brown and film star was Tom Cruise<br />
    then your unique identifier would be CBTC</span>"""))
    time.sleep(1.5)

    display(HTML(f"""<span style='{style_consent}'>Please enter your user ID below.</span>"""))
    looped = False
    
    # isalpha() checks if the string only contains letters. It will display an error message if the text is inputted wrong. Loop for validating the user ID input
    while True:
        text_widget = text_input("User ID: ")  # Getting the Text widget
        user_id = text_widget.value  # Getting the text input from the Text widget
        data_dict['user_id'] = user_id
        # Validating the user ID format
        if len(user_id) != 4 or not user_id.isalpha():
            clear_output(wait=True)
            # Error message for invalid input
            error_handling_style = "color: tomato; font-size: 20px; display: flex; justify-content: center; align-items: center;"
            display(HTML(f"""<span style='{error_handling_style}'>Please enter a valid user ID with exactly four letters, containing only letters.</span>"""))
        else:
            data_dict['user id'] = user_id
            break

    # Data consent request
    display(HTML(f"""<span style='{style_consent}'>Please read:<br /><br />
    We wish to record your response data to an anonymised public data repository.<br />
    Your data will be used for educational teaching purposes practising data<br /> 
    analysis and visualisation.<br />
    Results consent is necessary to continue.<br />
    Do you consent to the storage of your age, gender and results?</span>"""))
    # Consent checkboxes and confirm button - ensuring they are centered for visual appeal
    display_centered(personal_consent_checkbox)
    display_centered(results_consent_checkbox)
    confirm_button()

    # Error handling - handling the case where the user does not give consent
    if not (personal_consent_checkbox.value and results_consent_checkbox.value):
        display(HTML(f"""<span style='{style_consent}'>The user does not wish to share results.<br />
        The test cannot continue.</span>"""))
        raise SystemExit("Exiting the test... :(")  # Terminate the test!! We need consent to continue!
        return
    # Additional personal information requests
    personal_info_4 = 'Please provide some background information for an anonymised study. Thank you!'
    style_personal_info_2 = "color: plum; font-size: 20px; display: flex; justify-content: center; align-items: center;"
    display(HTML(f"<div style='{style_personal_info_2}'><span>{personal_info_4}</span></div>"))
    time.sleep(2)
    # Asking for user's age+gender
    personal_info_5 = 'How old are you?'
    display(HTML(f"<div style='{style_personal_info_2}'><span>{personal_info_5}</span></div>"))
    display_centered(age_dropdown)
    personal_info_5 = 'What is your gender?'
    display(HTML(f"<div style='{style_personal_info_2}'><span>{personal_info_5}</span></div>"))
    display_centered(gender_radiobuttons)

    # Processing the submission of age and gender
    submit_button(age_dropdown, gender_radiobuttons)
    clear_output(wait=False)

    # Message indicating the test is about to begin
    personal_info_6 = 'Thank you! The test will begin shortly.'
    display(HTML(f"<div style='{style_personal_info}'><span>{personal_info_6}</span></div>"))
    time.sleep(2)
    clear_output(wait=False)
    # Initiating the test countdown
    timer(timer_message)
    # Recording the test start time
    global test_start_time
    test_start_time = time.time() 

# Function to upload test results data to a Google Form
def upload_data():
    # Results data dictionary with user's answers
    results_data = {
    
        'answer': users_answers # Contains user's answers
    }
    
    # Converting the results data to a Pandas dataframe and then to JSON
    myresults = pd.DataFrame(results_data)
    results_json = myresults.to_json()
    
    # data dictionary to be sent to Google Forms
    data_dict = {
        'user_id': user_id, 
        'gender': gender,
        'age': age,
        'results': results_json, # User's test results in JSON format
        'test_time': total_test_time, # Total time taken for the test
        'score_as_percent': score_percentage, # User's score as a percentage
        'score_with_penalty': score_time # User's score adjusted for penalties
        }
    
     # URL of the Google Form where data will be uploaded
    form_url = 'https://docs.google.com/forms/d/e/1FAIpQLSeec7lgksjIePCmUxYP3KOo3Ww2NdeytOsWx-K2UiqQDbEfaw/viewform?usp=sf_link' 

    send_to_google_form(data_dict, form_url)


# Function to clear the output screen
def clear_screen():
    """
    Clears the output screen based on the operating system.
    """
    # Uses system command to clear the console
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to handle the submission of an answer and ensure the code continues running if a non-numerical value is input
def on_submit(their_answer):
    global correct, incorrect, times, current_index, start_time, users_answers
    

    # Error handling - Handling non-numerical input with an error message
    if their_answer == None:
        error_handling= 'Invalid input entered. Please only type numbers :)! Try again.'
        error_handling_style = "color: tomato; font-size: 20px; display: flex; justify-content: center; align-items: center;"
        display(HTML(f"<div style='{error_handling_style}'><span>{error_handling}</span></div>"))

        # Here we don't increment the current_index as we're retrying the current question.
        time.sleep(2)
        clear_output(wait=True)
        display_question(current_index)  # Redisplaying the same question
    else:
        # Processing the submitted answer
        time_to_answer = time.time() - start_time
        times.append(time_to_answer) # Append time for this question
    
        style_personal_info = "color: skyblue; font-size: 20px; display: flex; justify-content: center; align-items: center;"

        
        # Correct answer handling
        if their_answer == answers[current_index]:
            correct_answer_response = f"{answers[current_index]} is correct! :)"
            display(HTML(f"<div style='{style_personal_info}'><span>{correct_answer_response}</span></div>"))
            correct += 1
            users_answers.append(1)
        # Incorrect answer handling
        else:
            incorrect_answer_response = f"Incorrect :( The correct answer was: {answers[current_index]}"
            display(HTML(f"<div style='{style_personal_info}'><span>{incorrect_answer_response}</span></div>"))
            incorrect += 1
            users_answers.append(0)
            
        # Moving to the next question or ending the test
        if current_index < len(questions) - 1:
            current_index += 1
            time.sleep(2)
            clear_output(wait=True)
            display_question(current_index)  # Display next question
        else:
            calculate_score()

# Function to display the question using widgets
def display_question(index):
    """
    Displays each component of the question.
    
    Parameters:
    index: int, the index of the current question
    """
    global start_time
    question = questions[index]
    start_time = time.time()

    
    # Displaying each part of the question with a delay of 1.5 seconds
    for part in question.split():
        style = "color: palevioletred; font-size: 100px; display: flex; justify-content: center; align-items: center;"
        display(HTML(f"<div style='{style}'><span>{part}</span></div>"))
        time.sleep(1.5)
        clear_output(wait=True)


    # Get the text input from the Text widget
    answer_input= text_input("Answer: ")
    answer_text = answer_input.value.strip()  # Get the text input and remove leading/trailing whitespace


    if not answer_text.lstrip("-").isdigit():
        on_submit(None)
    else:
        ans_input_int = int(answer_text)
        on_submit(ans_input_int)
        
# Function to calculate and display the final score
def calculate_score():
    global total_test_time
    global score_percentage
    global score_time
    """
    Calculates the final score based on the number of correct and incorrect answers and the time taken.
    """
    
    # Calculating the score
    total_test_time = time.time() - test_start_time  # Total time for the test
    hypothesis_time = hypothesis_time_per_question * len(questions)
    time_difference = total_test_time - hypothesis_time

    # Apply penalty only if the total time taken is more than the hypothetical time
    if total_test_time > 4:
        hypothesis_time = hypothesis_time_per_question * len(questions)
        time_difference = total_test_time - hypothesis_time
        penalty = max(time_difference, 0) * 0.01  # 0.01 as the penalty rate
    else:
        penalty = 0

    # Calculate final score
    score_time = ((correct - penalty) / (correct + incorrect)) * 100
    score_percentage = (correct / (correct + incorrect)) * 100

    def compare_score(sheet_id):
        global position
        position = 0
        try:
            converted_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
            compare_score_data = pd.read_csv(converted_url)
            all_scores = compare_score_data['score_with_penalty'].dropna().tolist()
            all_scores.append(score_time)  # Add the user's score
            all_scores.sort(reverse=True)  # Sort scores in descending order
            position = all_scores.index(score_time) + 1  # Find user's position
            return all_scores
        except Exception as e:
            print(f"Error in compare_score: {e}")
            return []



    all_scores = compare_score(score_sheet)
    num_scores = len(all_scores)

    # Displaying final score and test completion messages
    test_over_message = f"Test completed in <b>{total_test_time:.2f}<b> seconds." 
    test_over_message_2 = f"You got: <b>{correct}<b> questions correct out of <b>{len(questions)} ({score_percentage:.2f}%<b>)"
    test_over_message_3 = f"Accounting for the time taken, your final score is <b>{score_time:.2f}%!<b> :)"
    test_over_message_4 = f"You placed {position} out of {num_scores} individuals!"

    style_finish_test = "color: pink; font-size: 40px; display: flex; justify-content: center; align-items: center;"
    display(HTML(f"<div style='{style_finish_test}'><span>{test_over_message}</span></div>"))
    display(HTML(f"<div style='{style_finish_test}'><span>{test_over_message_2}</span></div>"))
    display(HTML(f"<div style='{style_finish_test}'><span>{test_over_message_3}</span></div>"))
    display(HTML(f"<div style='{style_finish_test}'><span>{test_over_message_4}</span></div>"))
   


# Main test function
def run_math():
    personal_info()
    
    """
    Runs the math test by displaying each question and collecting answers.
    """
    display_question(0)  # Display first question
    upload_data()



# checkboxes used for consent
personal_consent_checkbox = widgets.Checkbox(value=False, description="I consent to the use of my gender and age", indent=False)
results_consent_checkbox = widgets.Checkbox(value=False, description="I consent to the use of my results", indent=False)
event_info = {
    'type': '',
    'description': '',
    'time': -1}

age_dropdown = widgets.Dropdown(
        options=[('Select Age', None)] + [(str(age), age) for age in range(18, 30)],
        value=None
    )
gender_radiobuttons = widgets.RadioButtons(
        options=['Male', 'Female', 'Other'],
        description='',
        disabled=False
    )

score_sheet= "1n1xNxaowMPoybbubz0kXA7uq18OhQLnefFDJV6nUVsY"


# Global variables
correct = 0
incorrect = 0
times = []
current_index = 0
hypothesis_time_per_question = 4
start_time = 0  # Start time for each question
test_start_time = 0  # Start time for the entire test
users_answers=[]
user_id=[]

questions = ['9 + 7', '13 - 20', '34 + 21', '56 - 28', '27 ÷ 9',
    '5 × 8', '56 ÷ 7', '8 × 11', '144 ÷ 12', '184 + 49',
    '135 ÷ 3', '13 × 7', '17 × 12', '119 + 37', '1091 - 195',
    '112 ÷ 16', '703 - 339']

answers = [16, -7, 55, 28, 3,
    40, 8, 88, 12, 233,
    45, 91, 204, 156, 896,
    7, 364]

data_dict = {'user id': '0', 'gender': 'NA', 'age': 'NA'}
