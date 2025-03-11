from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Gemini API Key
API_KEY = "AIzaSyAl--oZ-1BJD6CaCEy6jVePL21icn7Ulhw"

@app.route("/chatbot", methods=["POST"])
def chatbot():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"response": "Please provide a message."}), 400

    response = call_gemini_api(user_message)
    return jsonify({"response": response})

def call_gemini_api(message):
    url = "https://gemini.googleapis.com/v1/messages:generate"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    data = {
        "prompt": message,
        "maxTokens": 150  # Customize as needed
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        return response_data.get("choices", [{}])[0].get("text", "I couldn't process your request.")
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
