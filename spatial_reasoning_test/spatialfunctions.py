from IPython.display import display, HTML, Image, clear_output
from bs4 import BeautifulSoup
from jupyter_ui_poll import ui_events
from ipywidgets import Text, VBox, Button

import ipywidgets as widgets
import matplotlib.pyplot as plt
import pandas as pd
import requests
import json 
import time

def send_to_google_form(data_dict, form_url):
    ''' Helper function to upload information to a corresponding google form 
        You are not expected to follow the code within this function!
    '''
    form_id = form_url[34:90]
    view_form_url = f'https://docs.google.com/forms/d/e/{form_id}/viewform'
    post_form_url = f'https://docs.google.com/forms/d/e/{form_id}/formResponse'

    page = requests.get(view_form_url)
    content = BeautifulSoup(page.content, "html.parser").find('script', type='text/javascript')
    content = content.text[27:-1]
    result = json.loads(content)[1][1]
    form_dict = {}
    
    loaded_all = True
    for item in result:
        if item[1] not in data_dict:
            print(f"Form item {item[1]} not found. Data not uploaded.")
            loaded_all = False
            return False
        form_dict[f'entry.{item[4][0][0]}'] = data_dict[item[1]]
    
    post_result = requests.post(post_form_url, data=form_dict)
    return post_result.ok

def wait_for_event(timeout=-1, interval=0.001, max_rate=20, allow_interupt=True): 
    '''Event listener. Waits for defined event to occur, returns description and time values after event occurs.
    '''
    start_wait = time.time()

    # set event info to be empty as this is dict we can change entries directly without using the global keyword
    event_info['description'] = ""
    event_info['time'] = -1

    n_proc = int(max_rate*interval)+1
    
    with ui_events() as ui_poll:
        keep_looping = True
        while keep_looping==True:
            # process UI events
            ui_poll(n_proc)

            # end loop if we have waited more than the timeout period
            if (timeout != -1) and (time.time() > start_wait + timeout):
                keep_looping = False
                
            # end loop if event has occured
            if allow_interupt==True and event_info['description']!="":
                keep_looping = False
                
            # add pause before looping
            # to check events again
            time.sleep(interval)
    
    # return event description after wait ends will be set to empty string '' if no event occured
    return event_info


def register_btn_event(btn):
    '''Takes parameter btn, registers the event values associated with a button click. (description, time)
    '''
    event_info['type'] = "button click"
    event_info['description'] = btn.description
    event_info['time'] = time.time()
    return

def submit_button():
    '''Creates and displays 'Submit' button.
    '''
    confirm_btn = widgets.Button(description = "Submit")
    display(confirm_btn)
    confirm_btn.on_click(register_btn_event)
    wait_for_event()
    clear_output(wait = False)
    return

def run_introduction():
    '''Executes: text introduction to code, inputs for consent and biodata, test instruction text.
    '''
    global user_id, age, gender

    display(HTML("<span style ='color:black; font-size:40px;'>Welcome to the Spatial Reasoning Test!</span>"))

    time.sleep(1)
    clear_output()

    display(HTML("<span style ='color:black; font-size:20px;'>To start off, please consent to the use of your data for research purposes.</span>"))
    data_permission = widgets.RadioButtons(options=['Yes', 'No'], description='I consent', disabled=False)
    display(data_permission) # displays buttons that wait for user to click.
    submit_button() # creates and displays 'Submit' button.

    display(HTML("<span style ='color:black;'>Please create an anonymous ID.<br/> To generate an anonymous 4-letter unique user identifier please enter <br /> - two letters based on the initials (first and last name) of a childhood friend<br /> - two letters based on the initials (first and last name) of a favourite actor / actress<br /> e.g. if your friend was called Charlie Brown and film star was Tom Cruise, your unique identifier would be CBTC</span>"))
    user_id_prompt = Text(description = "UserID:")
    display(user_id_prompt)
    submit_button()
    user_id = user_id_prompt.value.upper() # records unique identifier, ensures all letters are capitalised

    display(HTML(f'<span>Great! Your unique identifier is: {user_id}</span>'))

    time.sleep(1.5)
    clear_output()

    display(HTML("<span>What is your age?"))
    age_dropdown = widgets.Dropdown(options=[('Select Age', None)] + [(str(age), age) for age in range(18, 30)], value=None)
    display(age_dropdown)
    submit_button()
    age = age_dropdown.value 

    display(HTML("<span>What is your gender?</span>"))
    gender_button = widgets.RadioButtons(options=['Male', 'Female', 'Other'], description='Select gender', disabled=False)
    display(gender_button)
    submit_button()
    gender = gender_button.value

    display(HTML(f"<span>Confirm: I am {age} years old and identify as {gender}"))
    submit_button()

    display(HTML(f"<span style ='font-size:30px;'>Thank you. You will now be directed to the test. </span>"))
    time.sleep(2)
    
    # Test instructions:
    display(HTML(f"<span style ='font-size:30px;'> There are {len(questions)} questions. </span>"))
    time.sleep(2)
    display(HTML(f"<span style ='font-size:20px;'>Questions will be shown one at a time: Your task is to select the 2D figure matching the large 3D figure.</span>"))
    time.sleep(3)
    display(HTML(f"<span style ='font-size:20px;'>Click A, B, C or D to record your answer.</span>"))
    time.sleep(3)
    display(HTML(f"<span style ='font-size:15px;'>Think carefully before answering!</span>"))
    time.sleep(3)

    clear_output()
    display(HTML(f"<span style ='font-size:30px;'>Test will begin in 3</span>"))
    time.sleep(1)
    clear_output()
    display(HTML(f"<span style ='font-size:30px;'>Test will begin in 2</span>"))
    time.sleep(1)
    clear_output()
    display(HTML(f"<span style ='font-size:30px;'>Test will begin in 1</span>"))
    time.sleep(1)
    clear_output()

    return user_id, age, gender

# questions dictionary: contains all questions
questions = {
    1: [Image("qn1_slide.png", width = 900), 'C'],
    2: [Image("qn2_slide.png", width = 900), 'B'],
    3: [Image("qn3_slide.png", width = 900), 'D'],
    4: [Image("qn4_slide.png", width = 900), 'A'],
    5: [Image("qn5_slide.png", width = 900), 'C'],
}

def next_question():
    '''Sets up and displays the next question of the quiz. Stops when progressed to the last question.
    '''
    global qn_number, start_time, correct_answer, total_questions
    
    total_questions = len(questions)
    
    if qn_number <= total_questions:
        # Get the next question and correct answer
        correct_answer = questions[qn_number][1]

        # Display the question and options
        display(HTML(f"<span style ='font-size:20px;'>Pick the option that does not match the Figure. </span>"))
        display(questions[qn_number][0])  # Index 0 holds the question image

def display_qn_button_panel(correct_answer):
    '''Defines and displays the button panel for selecting an option between A, B, C and D.
    Waits for user to click a button and records the description (aka the label) of the button.
    '''
    global qn_number, start_time, selected_option
    
    btnA = widgets.Button(description='A') # stores a created button with description 'A' in variable 'btnA'
    btnB = widgets.Button(description='B')
    btnC = widgets.Button(description='C')
    btnD = widgets.Button(description='D')

    btnA.on_click(register_btn_event) # calls register_btn_event if btnA is clicked.
    btnB.on_click(register_btn_event)
    btnC.on_click(register_btn_event)
    btnD.on_click(register_btn_event)
    
    panel = widgets.HBox([btnA, btnB, btnC, btnD]) # puts buttons in horizontal box
    display(panel)
    wait_for_event() 
    
    return 

# importing google sheet, creating pandas dataframe
def generate_user_statistics():
    ''' Imports Google sheet, converts it into a Pandas dataframe to execute:
        - Calculate average score
        - Rank user
        - Bar plot showing distribution of scores and user's standing
    '''
    
    sheet = "1630UlDrf93-svWmw25lxNPtcUilaEOZDu0FxdDm1Xgk"
    converted_url = f'https://docs.google.com/spreadsheets/d/{sheet}/export?format=csv' # reformats google sheet link to a format for code to access.
    spatial_df = pd.read_csv(converted_url) # read the CSV file from the URL.
    spatial_df = spatial_df.dropna(subset="Timestamp").iloc[:, 1:] # Removes irrelevant timestamp column from dataframe
    
    score_counter = 0 #sets score counter to 0
    spatial_scores = [] # creates list of spatial scores
    
    for i in spatial_df["result_recording"]: # for loop calculates (per response) how many questions answered correctly.
        for j in i.replace(",", "").split(): # splits information up as separate answers are denoted by ",".
            if j == "correct":
                score_counter += 1
        spatial_scores.append(score_counter)
        score_counter = 0
    
    spatial_df["score"] = spatial_scores
    
    # average score calculations
    average_score = spatial_df["score"].mean()
    display(HTML(f"The average score is {round(average_score,2)}")) # informs user their average score across all questions, rounded to 2 d.p.
    
    # ranking user's score and retrieving user's ranking
    spatial_ranked = spatial_df.sort_values(by = "score", ascending = False, ignore_index = True) # creates a new dataframe that has ranked the scores from highest to lowest.
    row_index = spatial_ranked.index.get_loc(spatial_ranked[spatial_ranked['user_id'] == data_dict['user_id']].index[0]) # retrieves user's rank
    
    display(HTML(f"You are ranked {row_index + 1} of {len(spatial_ranked)}")) # informs user of their ranking relative to other test-takers.
    
    # generating bar plot of all answers
    x = spatial_ranked["user_id"].astype(str).tolist() # converts dictionary values into a list
    y = spatial_ranked["score"].tolist()
    colors = ["black" if i != user_id else "red" for i in x] # highlights user's bar in red
    
    plt.bar(x,y,label="Bars 1",color = colors) # creates bar chart using lists stored in x and y.
    
    plt.xlabel("Score")
    plt.xticks(visible = False) # removes tick labels for anonymity
    plt.ylabel("Users, arranged high to low")
    plt.title("Where you stand:")
    plt.show() # displays bar chart for user to see

    return

def run_spatial_reasoning(): 
    '''Main function, executes entire sequence of spatial reasoning test.
    '''

    global event_info
    event_info = {'type': "",
                'description': "",
                'time': -1}

    run_introduction()

    # initialise result and time lists
    global result_recording, time_recording
     
    result_recording = [] # create empty lists for recording results later on
    time_recording = []

    # initialising questions
    global qn_number
    qn_number = 1
    
    while qn_number <= 5 : # executed this sequence as long as question number is less than total no. of questions
        next_question()
        
        start_time = time.time() # starts timer 
        
        display_qn_button_panel(correct_answer)
        selected_option = event_info["description"]
        
        end_time = time.time() # ends timer when user has selected an answer

        if selected_option == correct_answer: # informs user if selected answer was correct or wrong
            result_recording.append('correct')
            display(HTML(f"<span style ='font-size:20px; color: green;'>Correct</span style>"))
        else:
            result_recording.append('wrong')
            display(HTML(f"<span style ='font-size:20px; color: red;'>Wrong</span style>"))
        
        time.sleep(1)
        time_taken = end_time - start_time  # records time taken
        time_recording.append(time_taken) # uploads time to the list time_recording
        
        clear_output()
        qn_number += 1
        
    total_time = sum(time_recording) # records time taken to complete entire test
    
    # recording score
    count_correct = result_recording.count('correct')
    count_wrong = result_recording.count('wrong')
    
    # score calculations
    avg_time_recording = round(sum(time_recording) / len(time_recording),2) # calculates average time recording, rounds to 2 d.p.
    score_percentage = round(count_correct/len(questions) * 100, 2)

    display(HTML(f"<span style = 'font-size:20px;'>Test completed! You took {total_time:.2f} seconds to complete the test. </br>Correct: {count_correct}</br>Wrong: {count_wrong}</br>You obtained a {score_percentage}%</span>"))
    
    # uploading info to Google form
    global data_dict
    data_dict = {
        'user_id': user_id,
        'age': age,
        'gender': gender,
        'time_recording': time_recording,
        'result_recording': result_recording,
    }
    
    form_url = 'https://docs.google.com/forms/d/e/1FAIpQLScWK1ct97GZOKZM3t2HUJuAP1XJXfbttUrwfDBusMsdSjy23Q/viewform?usp=sf_link'

    if send_to_google_form(data_dict, form_url) == True: # executes data upload to google form
        display(HTML(f"<span style = 'font-size:15px;'>Data has been uploaded. Displaying feedback. </span>")) # informs user if data is successfully uploaded

    generate_user_statistics() # returns user statistics for test-taker's reference

    return