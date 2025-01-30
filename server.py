from flask import Flask, render_template, request, jsonify
import sys
from PyQt6.QtWidgets import QApplication
from DrawingApp import MainWindow

app = Flask(__name__)

# Store drawn bars
drawn_bars = []

@app.route('/')
def home():
    return render_template('index.html')  # Your frontend page (to be created)

@app.route('/add_bar', methods=['POST'])
def add_bar():
    data = request.json
    bar_info = {
        'type': data['type'],
        'length': data['length'],
        'position': data['position'],
    }
    drawn_bars.append(bar_info)
    return jsonify({"message": "Bar added successfully", "bars": drawn_bars})

@app.route('/get_bars', methods=['GET'])
def get_bars():
    return jsonify(drawn_bars)

@app.route('/clear_bars', methods=['POST'])
def clear_bars():
    drawn_bars.clear()
    return jsonify({"message": "All bars cleared"})

if __name__ == '__main__':
    app.run(debug=True)  # Run Flask on localhost:5000
