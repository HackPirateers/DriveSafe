import logging
from random import randint
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
import json
from keras.preprocessing import image
import numpy as np
import cv2
import urllib.request, json, time
import sys
import os
import urllib.request, json, time
import urllib.request, json, time
import time
import requests

app = Flask(__name__)

ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)


@ask.launch
def new_game():
    welcome_msg = render_template('welcome')

    return question(welcome_msg).reprompt(welcome_msg)


@ask.intent("TrafficIntent", convert={'origin': str, 'destination': str, 'departure': str, 'arrival': str})

def return_traffic_analysis(origin,destination,departure,arrival):
    import urllib.request, json, time
    endpoint = "https://maps.googleapis.com/maps/api/distancematrix/json?"
    api_key = "AIzaSyDh7AyHVeTuX5BM3gJPj5nUg0FiPEknmLo"
    origin = origin.replace(" ",",")
    print(origin,destination,departure,arrival)
    destination = destination.replace(" ",",")
    departure_hour = departure.split(":")[0]
    departure_minute = departure.split(":")[1]
    departure_time = float(departure_hour + "." + departure_minute)

    arrival_hour = arrival.split(":")[0]
    arrival_minute = arrival.split(":")[1]
    arrival_time = float(arrival_hour + "." + arrival_minute)
    dict_time = {}
    best_time = 0
    while departure_time < arrival_time:
        nav_request = 'origins={}&destinations={}&departure_time={}&mode={}&traffic_model={}&key={}'.format(origin,
                                                                                                            destination,
                                                                                                            int(
                                                                                                                time.mktime(
                                                                                                                    time.strptime(
                                                                                                                        '2018-03-26 ' + departure + ":00",
                                                                                                                        '%Y-%m-%d %H:%M:%S'))),
                                                                                                            "driving",
                                                                                                            "best_guess",
                                                                                                            api_key)
        request = endpoint + nav_request
        response = urllib.request.urlopen(request).read()
        data = json.loads(response.decode('utf-8'))
        output = (data['rows'][0]['elements'][0]['duration_in_traffic']["text"])
        time_hour = output.replace(" mins", "")
        time_hour = time_hour.replace(" hour ", ".")
        time_hour = time_hour.replace(" hours ", ".")
        time_hour = time_hour.replace(" min", "")
        time_hour = float(time_hour)
        num = departure_time + time_hour
        if (num - int(num)) >= 0.6:
            num += 1.0
            num = num - 0.6
            num = round(num, 2)
        if (num) < arrival_time:
            dict_time[departure_time] = time_hour
            best_time = departure_time
        departure_time += 0.25
        departure_time = round(departure_time, 2)
        if (departure_time - int(departure_time)) >= 0.6:
            departure_time += 1.0
            departure_time = departure_time - 0.6
            departure_time = round(departure_time, 2)
        if round((best_time-best_time//1), 2) >= 0.6:
            best_time += 1.0
            best_time -= 0.6
            best_time = round(best_time, 2)

    if ("The best time to leave is: " + (str(best_time).replace(".", ":"))) == "The best time to leave is: 0":
        return statement("Within the paremeters you inputted you will not reach your destination on time.")
    else:
        return statement("The best time to leave is: " + (str(best_time).replace(".", ":")))
@ask.intent("WeatherSafetyIntent",convert={'destination':str, 'origin':str})

def return_weather_analysis(destination, origin):
    import urllib.request, json, time
    destination_address = destination.replace(" ","+")
    origin_address = origin.replace(" ","+")
    endpoint = "https://maps.googleapis.com/maps/api/distancematrix/json?"
    api_key = "AIzaSyDh7AyHVeTuX5BM3gJPj5nUg0FiPEknmLo"

    nreq = 'origins={}&destinations={}&key={}'.format(origin_address, destination_address, api_key)
    req = endpoint + nreq
    resp = urllib.request.urlopen(req).read()
    dta = json.loads(resp.decode('utf-8'))

    destination_address = (dta["destination_addresses"][0]).split(",")[2].split(" ")[2]
    origin_address = (dta["origin_addresses"][0]).split(",")[2].split(" ")[2]

    origin_endpoint = "https://api.openweathermap.org/data/2.5/weather?"
    origin_key = "7487c4fa1078b870d628607a3e4e8ccb"
    origin_nav_request = 'zip={}&APPID={}'.format(origin_address,origin_key)
    origin_request = origin_endpoint + origin_nav_request
    origin_response = urllib.request.urlopen(origin_request).read()
    origin_data = json.loads(origin_response.decode('utf-8'))
    origin_weather = (origin_data["weather"][0]["id"])

    destination_endpoint = "https://api.openweathermap.org/data/2.5/weather?"
    destination_key = "7487c4fa1078b870d628607a3e4e8ccb"
    destination_nav_request = 'zip={}&APPID={}'.format(destination_address, destination_key)
    destination_request = destination_endpoint + destination_nav_request
    destination_response = urllib.request.urlopen(destination_request).read()
    destination_data = json.loads(destination_response.decode('utf-8'))
    destination_weather = (destination_data["weather"][0]["id"])

    if 781 == origin_weather or 781 == destination_weather or 900 <= origin_weather <= 902 or 900 <= destination_weather <= 902 or 905 <= origin_weather <= 906 or 905 <= destination_weather <= 906 or 957 <= origin_weather <= 962 or 957 <= destination_weather <= 962:
        return statement("Be careful of this extreme weather, I advise to definitely not drive outside.")
    elif 602 == origin_weather or 602 == destination_weather or 621 <= origin_weather <= 622 or 621 <= destination_weather <= 622:
        return statement("Be careful of the heavy snow, I recommend not driving outside currently")
    elif 600 <= origin_weather <= 601 or 600 <= destination_weather <= 601 or 611 <= origin_weather <= 620 or 611 <= destination_weather <= 620:
        return statement("Be careful of the sleet and light snow, make sure you are not speeding")
    elif 200 <= origin_weather <= 531 or 200 <= destination_weather <= 531:
        return statement("Be careful of the rain and thunder, make sure you are not speeding")
    else:
        return statement("The weather outside is safe and great to drive. Remember to buckle up and maintain control of the car")

@ask.intent("NoIntent")
def no_intent():
    return statement("Bye")


@ask.intent("TimeIntent", convert={'time': str})
def time_intent(time):
    return statement("Time is", time)


if __name__ == '__main__':
    app.run(debug=True)
