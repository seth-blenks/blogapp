from flask_wtf import csrf
from flask_wtf.csrf import validate_csrf as val
from functools import wraps
from wtforms.validators import ValidationError
from flask_login import login_required, current_user
from PIL import Image as PIL_Image
from threading import Thread
from uuid import uuid4
from flask import current_app, abort, redirect, url_for
from os import path, remove
from database import Image, sql
import logging
import math, random

logger = logging.getLogger('gunicorn.error')


 
# function to generate OTP
def generateOTP() :
 
    # Declare a digits variable 
    # which stores all digits
    digits = "0123456789"
    OTP = ""
 
   # length of password can be changed
   # by changing value in range
    for i in range(4) :
        OTP += digits[math.floor(random.random() * 10)]
 
    return OTP

def validate_csrf(csrf):
	if current_app.config['PERSONALTESTING']:
		return True
		
	try:
		val(csrf)
		return True
	except ValidationError:
		return False

def gen_csrf():
	return csrf.generate_csrf()


def admin_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if not (current_user.admin_authenticated and current_user.is_authenticated):
			abort(404)
		else:
			return f(*args, **kwargs)
	return wrapper

def password_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if current_user.is_authenticated:
			if not current_user.has_password():
				return redirect(url_for('set_password'))	
		return f(*args, **kwargs)
	
	return wrapper


def threaded_save(imagename, location):
	with open(path.join(location,imagename),'rb') as r_image:
		PIL_Image.open(r_image).resize((680,480)).save(path.join(location,imagename))

def save_image(image):
	filename = image.filename
	extension = filename.split('.')[-1]
	database_name = str(uuid4()) + '.' + extension
	direc = current_app.config['IMAGE_DIRECTORY']
	
	image.save(path.join(direc,database_name))
	Thread(target = threaded_save, args=(database_name,direc)).start()
	
	image_entry = Image(name=database_name)
	sql.session.add(image_entry)
	sql.session.commit()

	return database_name

def delete_image(image):
	try:
		remove(path.join(current_app.config['IMAGE_DIRECTORY'],image.name))
		logger.info(f'Delete {image.name} from file system')
		return True
	except FileNotFoundError:
		logger.error(f'{image.name} not found in filesystem!')
		return False