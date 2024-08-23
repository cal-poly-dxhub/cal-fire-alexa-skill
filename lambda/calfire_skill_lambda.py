# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.services import ServiceException
from ask_sdk_model.ui import AskForPermissionsConsentCard

from ask_sdk_model import Response
import requests
from bs4 import BeautifulSoup
import json

import os

LOCATION_API = 'https://calfireapi.azure-api.net/alexasearch/v1/sync_geometry_incident_search'
LOCATION_API_KEY = os.environ.get('API_KEY')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def getFires(address=None, lat=None, lon=None, rad=None):
    headers = {
        'Ocp-Apim-Subscription-Key': LOCATION_API_KEY
    } 
    params = {}

    if address is not None: 
        params["address"] = address 
    elif lat is not None and lon is not None: 
        params["lat"] = lat
        params["lon"] = lon

    if rad is not None:
        params["radiusMiles"] = rad

    print("here is the body we give it ", params) 

    response = requests.post(LOCATION_API, headers=headers, json=params)
    return response.json()



class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome, you can say Hello or Help. Which would you like to try?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)
    
    def handle(self, handler_input):
        def getLocation(handler_input):
            context = handler_input.request_envelope.context
            response_builder = handler_input.response_builder
            service_client_fact = handler_input.service_client_factory

            if context and "Geolocation" in context:
                return context.Geolocation
            elif context and (context.system.user.permissions and context.system.user.permissions.consent_token): 
                try:
                    device_id = context.system.device.device_id
                    device_addr_client = service_client_fact.get_device_address_service()
                    addr = device_addr_client.get_full_address(device_id)

                    if addr.address_line1 is None and addr.state_or_region is None:
                        response_builder.speak("Address has not been set")
                    else:
                        response_builder.speak("Your address is %s, %s, %s".format(
                            addr.address_line1, addr.state_or_region, addr.postal_code))
                    print(response_builder.response)
                    #return response_builder.response
                except ServiceException:
                    response_builder.speak("ERROR: Something went wrong while trying to access the device address. Please try again!")
                    return response_builder.response
                except Exception as e:
                    raise e
            else: 
                print(handler_input.request_envelope)
                response_builder.speak("You're missing necessary permissions")
                response_builder.set_card(
                    AskForPermissionsConsentCard(permissions=["read::alexa:device:all:address"]))
                print(response_builder.response)
                # return response_builder.response
        # type: (HandlerInput) -> Response
        speak_output = "Hello Python World from Inside the Intent Handler!"
        print("this is a print statement from inside the HelloWorldIntentHandler.")
        print(ask_utils.request_util.get_user_id(handler_input), "here is the user_id")

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class NotificationPermissionChangedEvent(AbstractRequestHandler):
    """Handler for notification permission changed event"""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AlexaSkillEvent.SkillNotificationSubscriptionChanged")(handler_input)
    def handle(self, handler_input): 
        # Extracting the request and context from handler_input
        request = handler_input.request_envelope.request
        context = handler_input.request_envelope.context
    
        # Extract user_id from the context
        user_id = context.system.user.user_id
    
        # Assuming 'subscriptions' is part of the request body in the custom event
        subscriptions = request.body.subscriptions
    
        # Implement your logic here based on the subscriptions update
        # For example, log the change, update a database, etc.
        print(f"User {user_id} changed subscriptions to: {subscriptions}")

class LearnMoreIntentHandler(AbstractRequestHandler): 
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("LearnMoreIntent")(handler_input)
    
    def handle(self, handler_input):
        print("invoked learnMoreIntent")
        print("it workeddd\n\n\n")
        speak_output = "You can learn how to get ready for wildfire at www.readyforwildfire.org. Would you like me to send the web address to your phone?"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        ) 
class FireNearXIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (handlerinput) -> bool
        return ask_utils.is_intent_name("FireNearXIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        area = slots['area'].value
        print("the area is ", area)
        
        fires = getFires(area, None, None, 80)

        incidents = fires['incidents']
        incidents.sort(key = lambda x: float(x['distanceMiles']))
        
        if len(incidents) == 0: 
            speak_output = f"there are no reported fires within 80 miles of {area}"
        else: 
            speak_output = f"we have found {len(incidents)} fires near {area}. the closest one is {incidents[0]['distanceMiles']} miles away"

        return  (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        ) 
class HowCloseIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (handlerinput) -> bool
        return ask_utils.is_intent_name("HowCloseIntent")(handler_input)
    def handle(self, handler_input):
        radius = 50
        loc = handler_input.request_envelope.context.geolocation.coordinate #same as the FireNearMeIntent TODO refactor
        fires = getFires(None, loc.latitude_in_degrees, loc.longitude_in_degrees, radius) 
        slots = handler_input.request_envelope.request.intent.slots
        fireName = slots['fireName'].value
        print(fireName)

        incidents = fires["incidents"] 
        print(len(incidents))
        
        flag = True
        for incident in incidents:
            if incident["incidentName"].lower() == fireName.lower(): 
                speak_output = f"the {fireName} fire is {incident['distanceMiles']} miles from you"
                flag = False 
        
        if flag:
            speak_output = f"we could not find any fires with the name {fireName} within {radius} miles of you"

        return  (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        ) 

class FireNearMeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (handlerinput) -> bool
        return ask_utils.is_intent_name("FireNearMeIntent")(handler_input)
    def handle(self, handler_input):
        loc = handler_input.request_envelope.context.geolocation.coordinate
        fires = getFires(None, loc.latitude_in_degrees, loc.longitude_in_degrees, 80)

        print("invoked FireNearMeIntent")
        speak_output = f"There are a total of {len(fires['incidents'])} fires within 80 miles of you "

        incidents = fires['incidents']
        incidents.sort(key = lambda x: float(x['distanceMiles']))
        
        speak_output += f"the closest one to you is named {incidents[0]['incidentName']} and is {incidents[0]['distanceMiles']} miles away"


        return  (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        ) 



class PreparednessWeekIntentHandler(AbstractRequestHandler): 
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        #print("invoked prep week intent")
        #context = handler_input.request_envelope.context
        #try:
        #    print("here is the location param", context.geolocation)
        #except:
        #    pass
 
        return ask_utils.is_intent_name("PreparednessWeekIntent")(handler_input)
    
    def handle(self, handler_input):
        speak_output = "Wildfire preparedness week is the first saturday of each May"
        try:
                # URL of the webpage you want to scrape
                url = 'https://www.nfpa.org/events/wildfire-community-preparedness-day'
        
                # Send an HTTP request to the URL
                response = requests.get(url)
                response.raise_for_status() # Raises an HTTPError if the HTTP request returned an unsuccessful status code
                
                # Parse the HTML content of the page with BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Locate the script or HTML tag containing the JSON object
                # This selector might need to be updated based on the webpage's structure
                scripts = soup.body.find('script')
                json_info = json.loads(str(scripts)[75:-9])
                date = json_info['props']['pageProps']['layoutData']['sitecore']['route']['placeholders']['storefront-main'][1]['fields']["content"]["value"][58:100]
                date = date.split("<")[0]
        except e:
            date = None 
        finally:
            if date is not None:
                speak_output += f" the website says that this is {date}"

        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        ) 



class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response

class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.

sb = CustomSkillBuilder(api_client=DefaultApiClient())

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(LearnMoreIntentHandler())
sb.add_request_handler(PreparednessWeekIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(FireNearMeIntentHandler())
sb.add_request_handler(FireNearXIntentHandler())
sb.add_request_handler(HowCloseIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

handler = sb.lambda_handler()
