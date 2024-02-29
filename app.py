from flask import Flask, request, jsonify
from pymongo import MongoClient
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from datetime import datetime
import requests
app = Flask(__name__) 
server = app
channelName = "#general"
slack_token = 'xoxb-6725827617664-6692113150615-UvfnFje8fY0PJvYeONGSnOx4'
slack_client = WebClient(token=slack_token)
slack_signing_secret = 'd5891134cb42f46cb8288c0cda2cca58'
slack_events_adapter = SlackEventAdapter(
    slack_signing_secret, "/slack/events", app)

client = MongoClient(
    'mongodb+srv://asdfasdf:asdfasdf@cluster0.q64wwy9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['birthday_db']
collection = db['birthdays']



@app.route('/send_birthday', methods=['POST'])
def create_birthday():
   
    try:
        data = request.json
        username = data['username']
        DOB= datetime.strptime(data["birthday"], "%d/%m/%Y")
        birthday = DOB
        collection.insert_one({'username': username, 'birthday': birthday})
        slack_client.chat_postMessage(
            channel=channelName, text=f"Birthday 🍭 reminder added for  {username} 😇")
        return jsonify({'message': 'Birthday created successfully'}), 201
    except:
        
        slack_client.chat_postMessage(
            channel=channelName, text=f"failed")
        return jsonify({'message': 'Birthday not created'}), 400


@app.route('/birthday', methods=['POST'])
def find_next_birthday():
   
    try:
        # print(request)
        dob_col=[]
        today = datetime.now()
        date=today.strftime("%d")
        month=today.strftime("%m")
        birthday= collection.find().sort('birthday', 1)
        for i in birthday:
            # print(not isinstance(i["birthday"],str))
            if (not (isinstance(i["birthday"] , str))) :
                if int(i['birthday'].strftime("%d"))>=int(date) or int(i['birthday'].strftime("%m"))>=int(month):
                    dob_col.append(i)
                    # print(i)
        
        # find days and months remaining until next birthday in dob_col
        for i in dob_col:
            if int(i['birthday'].strftime("%d"))>=int(date) or int(i['birthday'].strftime("%m"))>=int(month):
                next_birthday = i['birthday'].replace(year=today.year)
                if next_birthday < today:
                    next_birthday = next_birthday.replace(year=today.year + 1)
                days_to_go = (next_birthday - today).days
                i['days_to_go'] = days_to_go
                # send the post req to slack bot
                slack_client.chat_postMessage(
                    channel=channelName, text=f"Upcoming Birthday 🎂 for {i['username']} 🏂🏽 in {i['days_to_go']}  days to go ")
        return ("Advance Happy Birthday Everyone 🥳"), 200
    except:
        slack_client.chat_postMessage(
            channel=channelName, text=f"failed")
        return jsonify({'message': 'No Birthdays found'}), 400
            
    
   
   
#create route to delete
@app.route('/del_all_birthday', methods=['DELETE'])
def delete_all_birthday():
    try:
        collection.delete_many({})
        slack_client.chat_postMessage(
            channel=channelName, text="All Birthdays deleted 😎")
        return jsonify({'message': 'All Birthdays deleted successfully'}), 200
    except:
        slack_client.chat_postMessage(
            channel=channelName, text=f"failed")
        return jsonify({'message': 'All Birthdays not deleted'}), 400

#delete specific birthday
@app.route('/del_one_birthday', methods=['POST'])
def delete_birthday():
    try:
        data = request.json
        username = data['username']
        collection.delete_one({'username': username})
        slack_client.chat_postMessage(
            channel=channelName, text=f"Birthday 🍭 reminder deleted for  {username} 😇")
        return jsonify({'message': 'Birthday deleted successfully 😼'}), 200
    except:
        slack_client.chat_postMessage(
            channel=channelName, text=f"failed")
        return jsonify({'message': 'Birthday not deleted'}), 400

#update the birthday
@app.route('/update_birthday', methods=['PUT'])
def update_birthday():
    try:
        data = request.json
        username = data['username']
        DOB= datetime.strptime(data["birthday"], "%d/%m/%Y")
        birthday = DOB
        collection.update_one({'username': username}, {'$set': {'birthday': birthday}})
        return jsonify({'message': 'Birthday updated successfully'}), 200
    except:
        slack_client.chat_postMessage(
            channel=channelName, text=f"failed")
        return jsonify({'message': 'Birthday not updated'}), 400
#check for today birthday
@app.route('/today_birthday', methods=['GET'])
def today_birthday():
    try:
        today = datetime.now()
        # print("today",today)
        date=today.strftime("%d")
        month=today.strftime("%m")
        birthday= collection.find()
        for i in birthday:
            if int(i['birthday'].strftime("%d"))==int(date) and int(i['birthday'].strftime("%m"))==int(month):
                slack_client.chat_postMessage(
                    channel=channelName, text=f"Happy Birthday 🎂🎂🎂🎂🎂{i['username']} 🥳")
        return jsonify("Mesage sent to slack"), 200
    except:
        slack_client.chat_postMessage(
            channel=channelName, text=f"failed")
        return jsonify({'message': 'No Birthdays found'}), 400


@slack_events_adapter.on("message")
def handle_message(event_data):
   # send message whatever we sent send in slack
    message = event_data["event"]
   
    st=message.get("text")
    arr=st.split("-")
    # print(arr)
    try:
        if arr[0]=="shinigami" and arr[1]=="add":
            data = {
                "username": arr[2],
                "birthday": arr[3]
            }

            #call the api route
            response = requests.post("http://127.0.0.1:5000/send_birthday", json=data)
        if arr[0]=="shinigami" and arr[1]=="del":
            data = {
                "username": arr[2]
            }
            response = requests.post("http://127.0.0.1:5000/del_one_birthday", json=data)
        if arr[0]=="shinigami" and arr[1]=="delall":
            response = requests.delete("http://127.0.0.1:5000/del_all_birthday")
        if arr[0]=="shinigami" and arr[1]=="update":
            data = {
                "username": arr[2],
                "birthday": arr[3]
            }
            response = requests.put("http://127.0.0.1:5000/update_birthday",json=data)
        
      
        
            

    except:
        print("error")

 
    
   

    # if message.get("subtype") is None and message.get("text") is not None:
    #     user = message.get("user")
    #     channel = message["channel"]
    #     text = message["text"]
      
    #     if user != "U06LC3B4EJ3":
    #         slack_client.chat_postMessage(channel=channel, text=text)   
    #     return jsonify({'message': 'Message sent successfully'}), 200




if __name__ == "__main__":
    app.run(debug=False,port=5000)
