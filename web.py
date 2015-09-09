# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
from LCD import LCD
import subprocess
import os

app = Flask(__name__)
lcd = LCD()
lcd.init(C=False, B=False)
lcd.clear()

@app.route("/")
def Index():
    return render_template("index.html")



@app.route("/api/LCD")
def _writeLCD():
    data = request.args
    lcd.clear()
    for i in range(4):
        lcd.moveLine(i)
        lcd.writeText(data["line"+str(i+1)])
    subprocess.call(["fswebcam","/home/pi/FlaskLCD/static/out.jpg"])
    return jsonify(data="success")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
