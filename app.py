from flask import Flask, render_template, request, redirect, url_for 
import requests

app = Flask(__name__)

WEBEX_API_BASE = 'https://webexapis.com/v1'

def get_user_info(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f'{WEBEX_API_BASE}/people/me', headers=headers)
    if response.status_code == 200:
        return response.json()  # User information
    else:
        return None  # Invalid token

def get_rooms(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f'{WEBEX_API_BASE}/rooms', headers=headers)
    if response.status_code == 200:
        return response.json().get('items', [])  # List of rooms
    else:
        return None

def send_message_to_room(access_token, room_id, message):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "roomId": room_id,
        "text": message
    }
    response = requests.post(f'{WEBEX_API_BASE}/messages', json=data, headers=headers)
    return response.status_code == 200  # Return True if successful

# Home route for logging in
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        access_token = request.form.get('access_token')
        user_info = get_user_info(access_token)
        if user_info:
            return render_template('menu.html', user_info=user_info, access_token=access_token)
        else:
            return "Invalid access token. Please try again.", 400
    return render_template('index.html')

# Menu route that shows after login
@app.route('/menu/<access_token>', methods=['GET'])
def menu(access_token):
    user_info = get_user_info(access_token)
    rooms = get_rooms(access_token)  # Ensure you fetch the rooms here
    if user_info:
        return render_template('menu.html', user_info=user_info, access_token=access_token, rooms=rooms)
    else:
        return "Invalid access token.", 400

# Example route to show rooms
@app.route('/rooms/<access_token>', methods=['GET'])
def rooms(access_token):
    rooms = get_rooms(access_token)
    if rooms is not None:
        return render_template('rooms.html', rooms=rooms, access_token=access_token)
    else:
        return "Failed to retrieve rooms.", 400

# Route to send message to a room
@app.route('/send_message/<access_token>', methods=['POST'])
def send_message(access_token):
    room_id = request.form.get('room_id')
    message = request.form.get('message')
    if send_message_to_room(access_token, room_id, message):
        return redirect(url_for('rooms', access_token=access_token))  # Redirect to rooms
    else:
        return "Failed to send message.", 400

# Additional menu options
@app.route('/test_connection/<access_token>', methods=['GET'])
def test_connection(access_token):
    user_info = get_user_info(access_token)
    if user_info:
        return "Connection to Webex is successful!", 200
    else:
        return "Connection failed.", 400

if __name__ == '__main__':
    app.run(debug=True)
