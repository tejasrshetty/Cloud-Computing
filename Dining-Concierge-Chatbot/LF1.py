
import logging
import os
import dateutil.parser
import datetime
import time
import boto3


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']
    
def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }

def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False

def validate_order_restaurants(location,cusine,drinks, date,street, phone_number, no_of_people ):
    location_list = ['new york']
    location_list_str = ("," .join(location_list))
    if location is not None and location.lower() not in location_list:
        return build_validation_result(False,
                                       'Location',
                                       'We do not have recommendations for restaurants in {}, We currently supprt '
                                       'the following locations: \n {}'.format(location, location_list_str))

    if cusine is not None:
        if str(cusine).isnumeric():
            return build_validation_result(False,
                                           'Cusine',
                                           'The input cusine {} is invalid as it contains numbers. '
                                           'Please enter a valid cusine'
                                           .format(str(cusine)))
    if drinks is not None:
        if str(drinks).isnumeric():
            return build_validation_result(False,
                                           'Drinks',
                                           'The input drink {} is invalid as it contains numbers. '
                                           'Please enter a valid drink'
                                           .format(str(drinks)))
    if date is not None:
        # Handle if date is today or tomorrow and handle for date formats other than mm--dd-yyyy
        if not isvalid_date(date):
            return build_validation_result(False, 'Date', 'I did not understand that, what date would you like '
                                                          'to book a reservation? '
                                                          'Please enter date in the format MM-DD-YYYY (with hyphens)' )
        elif datetime.datetime.strptime(date, '%Y-%m-%d').date() < datetime.date.today():
            return build_validation_result(False, 'Date', 'You can book restaurants from today. The date entered is not valid   '
                                                          'What day would you like to book a table?')

    if phone_number is not None:
        phone_number = str(phone_number)
        if not phone_number[0:2] == "+1":
            return build_validation_result(False, 'Phone_Number', 'The phone number entered does not have the country '
                                                                  'code or is not a US phone number.  '
                                                                  'Please enter a US number starting with +1')
        phone_number = phone_number[2 :]
        if not int(phone_number) or len(phone_number) != 10:
            if not phone_number[0:1] == "+1":
                return build_validation_result(False, 'Phone_Number',
                                               'The phone number entered is not a valid phone number '
                                               'Please enter a US number starting with +1')

    if no_of_people is not None:
        if not int(no_of_people):
            return build_validation_result(False, 'No_of_people',
                                           'The no of people entered is not a number '
                                           'Please enter a number')
        if int(no_of_people) <1:
            return build_validation_result(False, 'No_of_people',
                                           'The no of people entered is less than 1 '
                                           'Please enter a number greater than 1')
    # Tejas
    # Pick up time not considered currently

    # if pickup_time is not None:
    #     if len(pickup_time) != 5:
    #         # Not a valid time; use a prompt defined on the build-time model.
    #         return build_validation_result(False, 'PickupTime', None)
    #
    #     hour, minute = pickup_time.split(':')
    #     hour = parse_int(hour)
    #     minute = parse_int(minute)
    #     if math.isnan(hour) or math.isnan(minute):
    #         # Not a valid time; use a prompt defined on the build-time model.
    #         return build_validation_result(False, 'PickupTime', None)
    #
    #     if hour < 10 or hour > 16:
    #         # Outside of business hours
    #         return build_validation_result(False, 'PickupTime', 'Our business hours are from ten a m. to five p m. Can you specify a time during this range?')

    return build_validation_result(True, None, None)



def dining_suggestions(intent_request):
    """
    Performs dialog management and fulfillment for ordering flowers.
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """

    location = get_slots(intent_request)["Location"]
    cusine = get_slots(intent_request)["Cusine"]
    drinks = get_slots(intent_request)['Drinks']
    date = get_slots(intent_request)["Date"]
    street = get_slots(intent_request)["Street"]
    phone_number = get_slots(intent_request)["Phone_Number"]
    no_of_people = get_slots(intent_request)["No_of_people"]
    source = intent_request['invocationSource']


    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)

        validation_result = validate_order_restaurants(location, cusine, drinks, date, street, phone_number, no_of_people)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        # Pass the price of the flowers back through session attributes to be used in various prompts defined
        # on the bot model.
        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
        # if flower_type is not None:
        #     output_session_attributes['Price'] = len(flower_type) * 5  # Elegant pricing model

        return delegate(output_session_attributes, get_slots(intent_request))

    # Order the flowers, and rely on the goodbye message of the bot to define the message to the end user.
    # In a real bot, this would likely involve a call to a backend service.
    sqs = boto3.resource('sqs', 'us-east-1')

    queue = sqs.get_queue_by_name(QueueName='ChatbotAssignmentQ1')
    test_body = {
        "Date": date,
        "Cusine": cusine,
        "Drinks": drinks,
        "Location": location,
        "No_of_people": no_of_people,
        "Phone_Number": phone_number,
        "Street": street
    }

    response = queue.send_message(MessageBody=str(test_body))



    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Thanks, your order for restaurants in {} has been recorded '
                             'We will notify you details via a message on {}'.format(location, phone_number)})

def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestionsIntent':
        return dining_suggestions(intent_request)
    # raise Exception('Intent with name ' + intent_name + ' not supported')

def lambda_handler(event, context):
#     # TODO implement
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)