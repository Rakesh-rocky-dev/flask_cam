import board
import json
import busio
import adafruit_adxl34x
import time
from datetime import datetime

from flask import Flask,render_template,Response
import cv2

app=Flask(__name__)
camera=cv2.VideoCapture(0)


@app.route("/")
def index():
    return render_template("index.html")

def generate_frames():
    while True:

        ## read the camera frame
        success,frame=camera.read()
        if not success:
            break
        else:
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def accelerometer():
  i2c = busio.I2C(board.SCL, board.SDA)
  accelerometer = adafruit_adxl34x.ADXL345(i2c)

  while True:
      data = accelerometer.acceleration
      #list(data)
      return data[2]
      time.sleep(1)


def generate_random_data():
    while True:
        json_data = json.dumps(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "value": float(accelerometer()),
            }
        )
        yield f"data:{json_data}\n\n"
        time.sleep(1)


@app.route("/chart-data")
def chart_data():
    return Response(generate_random_data(), mimetype="text/event-stream")

@app.route('/live_feed')
def live_feed():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, threaded=True)