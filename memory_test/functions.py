import requests 
from bs4 import BeautifulSoup
import json
import firebase_admin
from firebase_admin import credentials, db

#This is the function that sends the data to the google form

def send_to_google_form(data_dict, form_url):

    '''
    This function will take in my data that i want to send tho the google and my form URL.

    The function will push the data to the google form if there are no errors 
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

#This is the function that finds my firebase database

def initialize_firebase_app():
    '''
    This function checks if there is a firebase app initialized, if there isnt then a new app is initialized

    We are accessing the app through my secret key and then linking it to the firebase web URL
    '''
    
    if not firebase_admin._apps:
        cred = credentials.Certificate('bios30-7c9dc-firebase-adminsdk-tmide-ec41747b67.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://bios30-7c9dc-default-rtdb.firebaseio.com/'
        })
