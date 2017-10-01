from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
from random import randint
import os
import time
import datetime
import glob
import subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
temp_sensor = '/sys/bus/w1/devices/28-000008389b9b/w1_slave'

def tempsensor():
	catdata = subprocess.Popen(['cat',temp_sensor], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out,err = catdata.communicate()
	out_decode = out.decode('utf-8')
	lines = out_decode.split('\n')
	return lines	

def tempread(lines):
	temp_output = lines[1].find('t=')
	if temp_output != -1:
		temp_string = lines[1][temp_output+2:]
		temp_c = float(temp_string)/1000.0
		temp = round(temp_c, 1)
		return temp

@app.route('/') 
def index():
	return render_template('temp.html')

@socketio.on('message')
def handleMessage(msg):
#	print('Message: ' + msg)	
	lines = tempsensor()
	temp = tempread(lines)
	#counter = randint(0,9)
	send(temp, broadcast=True)

@socketio.on('my event')
def handle_my_custom_event(json):
	emit('my response', {'data' : 42})

if __name__ == '__main__':
	socketio.run(app, host='0.0.0.0', port=8181)
