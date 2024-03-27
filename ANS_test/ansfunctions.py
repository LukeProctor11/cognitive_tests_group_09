import time
from IPython.display import display, Image, clear_output, HTML
import ipywidgets as widgets
from ipywidgets import HBox, VBox, Layout
from jupyter_ui_poll import ui_events
import requests
from bs4 import BeautifulSoup
import json 
import pandas as pd

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

def send_to_google_form(data_dict, form_url):
    '''
    Sends data from the results dictionary to the google form.
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

def weber_calc(ratios):
    '''
    Calculates the weber fracions for each image. 
    Each ratio is split into the larger number (left) and the smaller number (right) separated by ':'.
    '''
    weber_fractions = []
    for i in ratios:
        num1, num2 = map(int, i.split(':'))
        weber = (num1 - num2) / num2
        weber_fractions.append(f'{weber:.4f}')

    return weber_fractions  

def compare_score(sheet_id):
    '''
    Stores the data from everyone's results by accessing the google sheet.
    Stores everyone's scores as a list, and removes any values of nan formed from
    empty data in sheets.
    Calculates the user's relative position compared to the other users.
    Returns everyone's scores
    '''
    converted_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
    sheet_data = pd.read_csv(converted_url)   
    pre_all_scores = list(sheet_data['score'])
    all_scores = [x for x in pre_all_scores if str(x) != 'nan']
    global position
    position = 0
    for i in all_scores:
        if i <= count_correct_ans:
            position += 1

    return all_scores

def wait_for_event(timeout=-1, interval=0.001, max_rate=20, allow_interupt=True):    
    '''
    Code waits until either the user has timed out or has completed an input.
    The input will result in the change of the event description.
    '''
    start_wait = time.time()

    # reset event info
    event_info['type'] = ""
    event_info['description'] = ""
    event_info['time'] = -1

    n_proc = int(max_rate*interval)+1
    
    with ui_events() as ui_poll:
        keep_looping = True
        while keep_looping==True:

            # process UI events
            ui_poll(n_proc)

            # end the loop if the time spent looping is longer than the timeout period. -1 can be set for no timeout
            if (timeout != -1) and (time.time() > start_wait + timeout):
                keep_looping = False

            # when the event_info description changes, stop looping
            if allow_interupt==True and event_info['description']!="":
                keep_looping = False

            # update the progress bar over time while looping
            ans_time_bar.value = time.time() - start_wait

    return event_info

def register_btn_event(btn):
    '''
    When the user clicks the button, change the event_info description to the button description.
    This will interupt the looping in wait_for_event.
    '''
    event_info['type'] = "button click"
    event_info['description'] = btn.description
    event_info['time'] = time.time()
    return

def register_text_input_event(text_input):
    '''
    When the user inputs text and presses enter, change the event_info description to the button description.
    This will interupt the looping in wait_for_event.
    '''
    event_info['type'] = "text_entry"
    event_info['description'] = text_input.value
    event_info['time'] = time.time()
    return

def text_input(prompt=None):
    '''
    Allows the user to input text via a text widget. 
    Code will continue once enter is pressed
    '''
    text_input = widgets.Text(description=prompt, style= {'description_width': 'initial'})
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    text_input.on_submit(register_text_input_event)
    display(text_input)
    event = wait_for_event()
    text_input.disabled = True
    return event['description']

def confirm_button():
    '''
    Displays confirm button which waits for the user to click
    '''
    display(confirm_btn)
    confirm_btn.on_click(register_btn_event)
    wait_for_event()
    clear_output(wait=False)
    return

def calculate_score():
    '''
    Calculates the score. The global variable count_correct_ans stores the 
    number of correct answers. Percentage score is then calculated from
    the total number of scores.
    '''    
    global count_correct_ans
    count_correct_ans = 0

    # counts number of correct answers
    for i in results_list:
        count_correct_ans += i

    # percentage score calculation
    percent_score = round((count_correct_ans / images_num) * 100)
    
    return percent_score

def test_setup():
    '''
    Sets up the test by asking user for user ID and consent.
    If no results consent is given, the function is terminated early.
    If details consent i given, ask the user for age and gender
    via a series of widgets.
    '''
    display(HTML(f"""<span style='{style1}'>Welcome to the ANS test, where we will test your ability to 
    quickly distinguish between similar numbers of dots.</span>"""))

    time.sleep(3)
    
    id_instructions = """
    Enter your anonymised ID

    To generate an anonymous 4-letter unique user identifier please enter:
    - two letters based on the initials (first and last name) of a childhood friend
    - two letters based on the initials (first and last name) of a favourite actor / actress

    e.g. if your friend was called Charlie Brown and film star was Tom Cruise
     then your unique identifier would be CBTC
    """

    print(id_instructions)
    time.sleep(2)

    display(HTML(f"""<span style='{style2}'>Please enter your user ID.</span>"""))
    looped = False
    
    # isalpha() checks if the string only contains letters. will remind user if inputted wrong
    while not data_upload['user id'].isalpha():
        if looped == True:
            display(HTML(f"""<span style='{style2}'>No numbers or special characters should be input.</span>"""))
        user_id = text_input("User ID: ")
        data_upload['user id'] = user_id
        clear_output(wait=True)
        looped = True

    print(f'User entered {user_id}')
    
    display(HTML(f"""<span style='{style2}'>Please read:<br /><br />
    We wish to record your response data to an anonymised public data repository.<br />
    Your data will be used for educational teaching purposes practising data<br /> 
    analysis and visualisation.<br />
    Results consent is necessary to continue.<br />
    Do you consent to the storage of your age, gender and results?</span>"""))

    display(details_check)
    display(results_check)
    confirm_button()

    # terminates function if results consent not given
    if results_check.value == False:
        display(HTML(f"""<span style='{style2}'>User does not wish to share results.<br />
        Test will not go ahead.</span>"""))
        return results_check.value
        
        
    # only allows questions regarding the details of the user to be displayed if details consent is given
    if details_check.value == True:

        display(HTML(f"""<span style='{style2}'>Please select the gender you identify as.</span>"""))
        display(gender_dropdown)
        confirm_button()
        data_upload['gender'] = gender_dropdown.value

        display(HTML(f"""<span style='{style2}'>Please select your age.</span>"""))
        display(age_slider)
        confirm_button()
        data_upload['age'] = age_slider.value

    display(HTML(f"""<span style='{style2}'>You will be shown a series of images with blue and yellow dots.<br />
    You have to quickly decide whether there are more blue dots on the left, or yellow dots on the right.<br />
    Press the respective button as quickly as you can within three seconds.<br />
    You will be scored based on the number of correct answers you give.<br />
    There will be {images_num} questions on this test.<br />
    Good luck!</span>"""))

    time.sleep(5)
    confirm_button()
    ans_time_bar.value = 0
    display(ans_time_bar)
    wait_for_event(timeout=3)
    ans_time_bar.description = 'Time:'
    clear_output(wait=True)
    
    display(HTML(f"<span style='{style3}'>BEGIN!</span>"))
    time.sleep(2)
    clear_output(wait=True)

    return results_check.value

def next_image(image_name, correct_ans, i):
    '''
    Loops through all images of the test.
    Displays each image and waits for the user to click either the left or right button within
    three seconds.
    '''
    # displays the next image, then replaces with a blank
    clear_output(wait=True)
    display(Image(image_name, width = 800))
    time.sleep(0.75)
    clear_output(wait=True)
    display(blank)
    
    # display time progress, buttons and wait until button press (or until 3 seconds have passed)
    ans_time_bar.value = 0
    display(ans_time_bar)
    options[0].on_click(register_btn_event)
    options[1].on_click(register_btn_event)
    display(option_btns)
    time_out = ""
    
    # records the time taken for the user to respond to 2 dp
    start_time = time.time()
    wait_for_event(timeout=3)
    response_time = time.time() - start_time
    response_time_list.append(f'{response_time:.2f}')
    
    # if the button press was correct, append 1 (as "correct"), otherwise append 0 (as 'incorrect') including if timed out.
    if event_info['description'] == "LEFT" and correct_ans == "l":
        results_list.append(1)
    elif event_info['description'] == "RIGHT" and correct_ans == "r":
        results_list.append(1)
    else:
        results_list.append(0)

    # can determine whether user timed out from the empty event description
    if event_info['description'] == "":
        time_out = "TIMEOUT. "

    clear_output(wait=True)

    # if this was the last image, end the function
    if images_list[-1] == image_name:
        return
    
    display(blank)
    display(HTML(f"<span style='{style3}'>{time_out} QUESTION {i+2}</span>"))
    time.sleep(1.5)
    
    return

def run_test():
    '''
    Runs the ANS test starting with consent, loops through all images,
    displays the final score and uploads the results to the google
    forms.
    '''
    results_consent = test_setup()
    if results_consent == False:
        return
        
    # loops test for all images in the list
    for i in range(images_num):
        next_image(images_list[i], images_ans[i], i)        
    
    display(HTML(f"<span style='{style3}'>FINISH!</span>"))

    percent_score = calculate_score()
    print(f"Congrats! You scored {percent_score}%!")
    all_scores = compare_score(sheet_id)
    num_scores = len(all_scores) + 1
    print(f"Your position compared to other people: {num_scores - position} out of {num_scores}!")

    # send to google form
    if results_consent == True:
        data_upload['score'] = count_correct_ans
        results = {'Image File': images_list, 'nl': nl, 'nr': nr, 'ratio': dot_ratios, 'weber': weber_fractions, 'correct': results_list, 'time taken': response_time_list}
        frame = pd.DataFrame(results)
        results_json = frame.to_json()
        data_upload['results'] = results_json
        send_to_google_form(data_upload, form_url)
    return

# variables, lists and widgets
images_list = []
results_list = []
response_time_list = []
data_upload = {'user id': '0', 'gender': 'NA', 'age': 'NA'}
images_ans = ['l', 'r', 'r', 'l', 'r', 'l', 'l', 'l', 'r', 'r', 'l', 'r', 'r', 'l', 'r', 'l',
            "r", "l", "r", "l",	"l", "l", "l", "r",	"l", "r", "r", "l", "r", "r", "l", "l", 
            "r", "l", "l", "l", "r", "r", "l", "r", "r", "r", "l", "r", "l", "r", "r", "l",
            "r", "l", "l", "r", "r", "l", "r", "l", "l", "r", "r", "r", "l", "r", "l", "l"]

dot_ratios = ["16:12", "14:12", "18:16", "21:18", "12:9", "10:9", "20:18", "14:12",
          "10:9", "16:12", "18:16", "21:18", "20:15", "20:15", "20:18", "12:9",
          "12:9", "14:12", "16:12", "10:9", "16:12", "20:18", "21:18", "18:16",
          "18:16", "12:9", "10:9", "20:15", "20:18", "18:16", "12:9", "21:18",
          "21:18", "14:12", "16:12", "20:15", "14:12", "20:18", "18:16", "20:15",
          "10:9", "20:15", "12:9", "21:18",	"10:9", "14:12", "16:12", "20:18",
          "12:9", "20:15", "14:12", "18:16", "21:18", "21:18", "20:18", "16:12",
          "12:9", "14:12", "16:12", "20:15", "18:16", "10:9", "20:18", "10:9"]

nl = []
nr = []
weber_fractions = weber_calc(dot_ratios)
images_num = len(images_ans)

# make a list of all of the images, and stores how many dots are on the left and right into separate lists
for i in range(images_num):
    images_list.append(f"Test {i+1}.png")
    num1, num2 = map(int, dot_ratios[i].split(':'))
    if images_ans[i] == "r":   
        nr.append(num1)
        nl.append(num2)
    else:
        nl.append(num1)
        nr.append(num2)
                     
# styles used for HTML
style1 = "color: teal; font-size: 30px;"
style2 = "color: green; font-size: 20px;"
style3 = "color: yellow; font-size: 40px;"

# to display a blank image with no dots
blank = Image("Blank.png", width = 800)

# checkboxes used for consent
details_check = widgets.Checkbox(value=False, description="I consent to the use of my gender and age", indent=False)
results_check = widgets.Checkbox(value=False, description="I consent to the use of my results", indent=False)

# used for input of gender and age
gender_dropdown = widgets.Dropdown(options=["Male", "Female", "Other"], value="Male", description="Gender:")
age_slider = widgets.IntSlider(min=15, max=60, value=20, description="Age:")

# left and right buttons used for the test
options_descr = ['LEFT', 'RIGHT']
options = [widgets.Button(description=d, 
        style=dict(font_style='italic', font_size='70px'),
        layout=Layout(width='400px', height='150px')) for d in options_descr]
option_btns = HBox(options)

# button used to input confirmation from user
confirm_btn = widgets.Button(description = "Confirm")

# shows how much time is left to answer the question
ans_time_bar = widgets.FloatProgress(value=0, 
                                     min=0, 
                                     max=3, 
                                     description='Loading:', 
                                     bar_style='info', 
                                     style={'bar_color': '#ffef00'}, 
                                     orientation='horizontal'
                                    )
# used for the looping events
event_info = {
    'type': '',
    'description': '',
    'time': -1}

form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfcDBI7YUe5q9cPLngqcLZ8YDryfSbLHAv0kPgzFsGeg0gahQ/viewform?usp=sf_link"
sheet_id = "1s4RzdGzKZZVk9cRWwonmyb2iCF6ssd-w42vn0dGlyFo"