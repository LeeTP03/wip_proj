# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
from typing import Coroutine, Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, FollowupAction, ActiveLoop, SlotSet, AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import actions.database as database
import actions.genai as genai
from datetime import datetime, date, timedelta

dc = database.DatabaseConnection()
gai = genai.GenAI()
            
class ValidateExchangeShoeForm(FormValidationAction):
    
    def name(self) -> Text:
        return "validate_simple_shoe_exchange_form"
    
    def validate_customer_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value.isalpha():
            return {"customer_name": slot_value}
        else:
            dispatcher.utter_message(template="Your name should only contain alphabets")
            return {"customer_name": None}
    
    def validate_customer_phone(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value.isdigit():
            return {"customer_phone_number": slot_value}
        else:
            dispatcher.utter_message(template="Your phone number should only contain numbers")
            return {"customer_phone_number": None}
        
    def validate_shoe_size(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        ALLOWED_SIZES = ["6", "7", "8", "9", "10", "11", "12", "13", "14", "15"]
        if slot_value.isdigit() and slot_value in ALLOWED_SIZES:
            return {"shoe_size": slot_value}
        else:
            dispatcher.utter_message(template="Please enter your US shoe size")
            return {"shoe_size": None}
        
    def validate_new_shoe_size(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        ALLOWED_SIZES = ["6", "7", "8", "9", "10", "11", "12", "13", "14", "15"]
        if slot_value.isdigit() and slot_value in ALLOWED_SIZES:
            return {"new_shoe_size": slot_value}
        else:
            dispatcher.utter_message(template="Please enter your US shoe size")
            return {"new_shoe_size": None}
        
    def validate_shoe_color(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        ALLOWED_COLORS = ["black", "white", "red", "blue", "green", "yellow", "orange", "purple", "pink"]
        if slot_value.lower() in ALLOWED_COLORS:
            return {"shoe_color": slot_value}
        else:
            dispatcher.utter_message(template="It should be a color")
            return {"shoe_color": None}
        
    def validate_purchase_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value.isdigit():
            return {"purchase_date": slot_value}
        else:
            dispatcher.utter_message(template="Please enter the date of purchase")
            return {"purchase_date": None}
    
    def validate_purchase_outlet(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        ALLOWED_OUTLETS = ["online", "physical store"]
        if slot_value.lower() in ALLOWED_OUTLETS:
            return {"purchase_outlet": slot_value}
        else:
            dispatcher.utter_message(template="Please enter the purchase outlet")
            return {"purchase_outlet": None}
        
    def validate_shoe_model(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        ALLOWED_MODELS = ["sneakers", "boots", "sandals", "flats", "heels", "slippers"]
        if slot_value.lower() in ALLOWED_MODELS:
            return {"shoe_model": slot_value}
        else:
            dispatcher.utter_message(template="Please enter the shoe model")
            return {"shoe_model": None}
        
class ShoeExchangeAction(Action):
    
    def name(self) -> Text:
        return "action_shoe_exchange"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Coroutine[Any, Any, List[Dict[str, Any]]]:
        purchase_date = tracker.get_slot("purchase_date")
        shoe_size = tracker.get_slot("shoe_size").strip()[-1]
        new_shoe_size = tracker.get_slot("new_shoe_size").strip()[-1]
        
        date_object = datetime.strptime(purchase_date, "%d/%m/%Y").date()
        current_date =  datetime.now().date()
        size_dict = {
            "6" : 1,
            "7" : 0,
            "8" : 1,
            "9" : 2,
            "10" : 3,
            "11" : 4,
            "12" : 5,
            "13" : 6,
            "14" : 7,
            "15" : 8
        }
        two_weeks = timedelta(weeks=2)
        #See if time difference betwene date_object and current time is more than 2 weeks
        if abs(date_object - current_date) > two_weeks:
            dispatcher.utter_message("Sorry, you can only exchange within 2 weeks of purchase")
            return []
        
        if size_dict[new_shoe_size] < 1:
            dispatcher.utter_message("Thank you for your submission a Larrie personnel will get back to you latest by tomorrow.")
            return []
        
        dispatcher.utter_message("We will process the exchange.")
        return [SlotSet("stock_available", True), FollowupAction("simple_shoe_exchange_form_2")]
    
class CheckOrderStatusAction(Action):
    
    def name(self) -> Text:
        return "action_check_order_status"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Coroutine[Any, Any, List[Dict[Text, Any]]]:
        order_id = int(tracker.get_slot("order_id").strip()[-1])
        purchase_date = tracker.get_slot("purchase_date")

        order_information = dc.get_order_information(order_id)
        
        if order_information[1].lower() != "shipped":
            dispatcher.utter_message("Your order is not shipped yet, we will get back to you latest tomorrow")
            return []
        else:
            dispatcher.utter_message("Your order has been shipped, here are your tracking details")
            dispatcher.utter_message(f"Tracking ID: {order_information[0]}\nTracking URL: {order_information[2]}")
        return []
        

class ActionResetAllSlots(Action):

     def name(self) -> Text:
            return "action_reset_all_slots"

     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            return [AllSlotsReset()]
        
class ExchangeShoeFinal(Action):
    
    def name(self) -> Text:
        return "exchange_shoe_sizes_final_action"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Coroutine[Any, Any, List[Dict[Text, Any]]]:
        shoe_exchange_address = tracker.get_slot("shoe_exchange_address")
        
        dispatcher.utter_message(f"We will process the exchange and get back to you soon. Please return the shoes back to Larrie/Geox")
        
        return []
