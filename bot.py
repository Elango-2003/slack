import os
from slack import WebClient
from flask import Flask, request, jsonify
from dotenv import load_dotenv


app = Flask(__name__)

slack_client = WebClient(token="")

@app.route("/send-message", methods=["GET"])
def send_message():
 
    message = "Hii I'm elango"

  
    channel_id = "#notifications"  

   
    response = slack_client.chat_postMessage(channel=channel_id, text=message)

  
    if response["ok"]:
        return jsonify({"success": True, "message": "Message sent successfully!"}), 200
    else:
        return jsonify({"success": False, "error": response["error"]}), 500

if __name__ == "__main__":

    app.run(debug=True)
