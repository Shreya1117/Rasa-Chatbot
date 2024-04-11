# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
import requests

HOST = "localhost"
PORT = 8888
ENDPOINT = "message"

LLM_URL = f"http://{HOST}:{PORT}/{ENDPOINT}"

USER_ID = '12345'

#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

class action_llm(Action):
    def name(self) -> Text:
        return "action_llm"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]):
        name = tracker.get_slot('name')
        age = tracker.get_slot('age')
        location = tracker.get_slot('location')
        symptom_iter = tracker.get_latest_entity_values("symptom")
        symptom_list = list()
        for symptom in symptom_iter:
            symptom_list.append(symptom)
        symptom_string = ", ".join(symptom_list)
        USER_INFO = f'I am {name}, from {location}. I am {age} years old. My symptoms are: {symptom_string}.'
        # dispatcher.utter_message(text=f"Dispatching amazing llm to {name}, from {location} with {symptom_string}!!!")
        res = requests.post(LLM_URL, json={'user_id': USER_ID, 'user_info': USER_INFO, 'message': 'How do I know if I have cancer?'}, timeout=120)
        res = res.json()
        if res['status'] == 200:
            dispatcher.utter_message(text=res['response'])
        else:
            dispatcher.utter_message(text="Some error occurred, My bad...")
        return []

class ValidateSimpleDetailForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_simple_detail_form"

    def validate_gender(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> Dict[Text, Any]:
        gender = slot_value.lower().strip()
        if 'female' in gender or 'girl' in gender or 'woman' in gender:
            return {"gender": "female"}
        elif 'male' in gender or 'boy' in gender or 'man' in gender:
            return {"gender": "male"}
        else:
            dispatcher.utter_message(text=f'Please enter an appropriate gender.')
            return {"gender": None}

    def validate_age(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> Dict[Text, Any]:
        age = slot_value.lower().strip()
        if not age.isdigit():
            dispatcher.utter_message(text=f'Please enter a numeric value for age.')
            return {"age": None}
        return {"age": int(age)}
