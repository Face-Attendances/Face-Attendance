#Tạo API bằng Flask
from flask import Flask, request, jsonify
from db import save_attendance, get_attendance

app = Flask(__name__)

@app.route('/attendance/<mamon>', methods=['GET'])
def get_attendance_api(mamon):
    data = get_attendance(mamon)
    return jsonify(data)

@app.route('/attendance', methods=['POST'])
def post_attendance_api():
    data = request.json
    if not all(k in data for k in ('id', 'name', 'mamon', 'time')):
        return jsonify({'error': 'Missing data'}), 400
    save_attendance(data['id'], data['name'], data['mamon'], data['time'])
    return jsonify({'message': 'Saved successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)
