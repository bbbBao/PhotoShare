######################################
# Written by Tianyi Bao <tianyib@bu.edu>
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

from email import message
import time
import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'bao1tian2' # ENTER YOUR DATABASE PASSWORD HERE
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		first_name=request.form.get('first_name')
		last_name=request.form.get('last_name')
		birth_date=request.form.get('birth_date')
		hometown=request.form.get('hometown')
		gender=request.form.get('gender')

	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Users (email, password, first_name, last_name, birth_date, hometown, gender) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(email, password, first_name, last_name, birth_date, hometown, gender)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT data, photo_id, caption FROM Photos WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

def getTopContribute():
	cursor = conn.cursor()
	cursor.execute("SELECT *  FROM Users ORDER BY contribution DESC LIMIT 10")
	return cursor.fetchall()

def getTopTag():
	cursor = conn.cursor()
	cursor.execute("SELECT name, COUNT(*) FROM Tags GROUP BY name ORDER BY COUNT(*) DESC LIMIT 5")
	return cursor.fetchall()

@app.route('/profile')
@flask_login.login_required
def protected():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile", photos=getUsersPhotos(uid),base64=base64, tags = getUserTags(uid))

def getAllStrangers(user_id):
	#user_id = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Users WHERE user_id != '{0}' AND user_id NOT IN (SELECT F.user_id2 FROM Friends F WHERE F.user_id1 = '{0}')".format(user_id))
	users = cursor.fetchall()
	res = []
	for user in users:
		if user[3] != 'UUUU@AAA':
			res.append(user)
	return res

def getAllFriends(user_id):
	#user_id = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT U.first_name, U.last_name, U.birth_date, U.hometown, U.gender, F.user_id2, U.email FROM Friends F, Users U WHERE F.user_id1 = '{0}' AND F.user_id2 = U.user_id".format(user_id))
	return cursor.fetchall()

def getFriendRecom(user_id):
	friends = getAllFriends(user_id)
	friendlist = ()
	res = []
	for friend in friends:
		friendlist = friendlist + getAllFriends(friend[5])
	for friend in friendlist:
		if friend not in res and friend[5] != user_id and friend not in friends:
			res.append(friend)
	return res

"""
def getFriendList(friends):
	friendid = []
	for friend in friends:
		friendid.append(friend[5])
	return friendid
"""

@app.route("/friend", methods=['GET', 'POST'])
@flask_login.login_required
def friend():
	user_id1 = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		
		user_id2 = request.form.get('addFriend')
		#friendid = getFriendList(getAllFriends())
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Friends (user_id1, user_id2) VALUES ('{0}', '{1}')".format(user_id1, user_id2))
		conn.commit()
	return render_template('friend.html', strangers=getAllStrangers(user_id1), friends=getAllFriends(user_id1), friendrecom = getFriendRecom(user_id1)) 

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def addTags(tags):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT MAX(photo_id) FROM Photos")
	pid = cursor.fetchone()[0]
	for tag in tags.split(', '):
		cursor.execute("INSERT INTO Tags (photo_id, name) VALUES ('{0}', '{1}')".format(pid, tag))
	conn.commit()

def getTags():
	cursor = conn.cursor()
	cursor.execute("SELECT DISTINCT *  FROM Tags GROUP BY name") 
	return cursor.fetchall()

def getUserTags(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT DISTINCT T.tag_id, T.photo_id, T.name, P.photo_id, P.user_id FROM Tags T, Photos P WHERE T.photo_id = P.photo_id AND P.user_id = '{0}' GROUP BY T.name".format(uid)) 
	return cursor.fetchall()

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		tags = request.form.get('tag')
		albumid = int(request.form.get('Album ID'))
		photo_data =imgfile.read()

		if isAlbumExist(albumid):
			print("Album Exist")
			if isAlbumBelong(albumid, uid):
				print("Album Belongs to Owner")	
				cursor = conn.cursor()
				cursor.execute('''INSERT INTO Photos (data, user_id, caption, albums_id) VALUES (%s, %s, %s, %s )''' ,(photo_data,uid, caption, albumid))
				cursor.execute("UPDATE Users SET contribution = contribution + 1 WHERE user_id = '{0}'".format(uid))
				conn.commit()
				addTags(tags)
				print('upload successfully')
				return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid),base64=base64)
			else:
				print("Album does not belongs to owner")
				return render_template('hello.html')
		else:
			print("Album does not Exist")
			return render_template('hello.html')

	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html')
#end photo uploading code

def checkAllPhotos(name):
	cursor.execute("SELECT P.data, P.caption, U.first_name, U.last_name FROM Photos P, Tags T, Users U WHERE P.photo_id = T.photo_id AND T.name='{0}' AND P.user_id = U.user_id".format(name))
	return cursor.fetchall()

def checkUserPhotos(name):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor.execute("SELECT P.data, P.caption, U.first_name, U.last_name FROM Photos P, Tags T, Users U WHERE P.photo_id = T.photo_id AND T.name='{0}' AND P.user_id='{1}' AND P.user_id = U.user_id".format(name,uid))
	return cursor.fetchall()

@app.route('/tags', methods=['GET', 'POST'])
def tag():
	"""
	try:
		uid = getUserIdFromEmail(flask_login.current_user.id)
	except:
		"""
	name = request.form.get('checkPhotos')
	return render_template('tags.html', tags = getTags(), photos=checkAllPhotos(name),base64=base64)
	"""
	else:
		#if request.form.get('checkPhotos') is not None:
		name = request.form.get('checkPhotos')
		return render_template('tags.html', tags = getUserTags(uid), photos=checkUserPhotos(name),base64=base64) 
	"""

@app.route('/viewphotos', methods=['GET', 'POST'])
def viewphotos():
	name = request.form.get('checkPhotos')
	return render_template('viewphotos.html', photos=checkUserPhotos(name),base64=base64)

def searchTag(tagstring):
	photo=()
	res = []
	for tag in tagstring.split(' '):
		photo = photo + checkAllPhotos(tag)
	for i in photo:
		if i not in res:
			res.append(i)
	return res

@app.route("/tagsearch", methods=['GET', 'POST'])
def tag_search():
	if request.method == 'POST':
		if request.form.get('tag') is not None:
			tagstring = request.form.get('tag')
			return render_template('tagsearch.html', photos = searchTag(tagstring),base64=base64) 
	return render_template('tagsearch.html')

def getPhotoRecom():
	cursor = conn.cursor()
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor.execute("SELECT P.data, P.caption ,P.photo_id FROM Tags T, Photos P, (SELECT T.name AS name2 FROM Tags T, Photos P WHERE T.photo_id = P.photo_id AND P.user_id ='{0}' GROUP BY T.name ORDER BY COUNT(*) DESC limit 5)  AS userTags ,(SELECT photo_id AS photo_id2, COUNT(*) AS numberofTag FROM Tags GROUP BY photo_id ORDER BY COUNT(*))  AS numTag WHERE T.name=name2 AND T.photo_id = P.photo_id AND T.photo_id = photo_id2 AND P.user_id<>'{0}' GROUP BY T.photo_id ORDER BY COUNT(*) DESC, numberofTag".format(uid))
	mayLikePhotos = cursor.fetchall()
	return mayLikePhotos
		
@app.route('/photorecom', methods=['GET', 'POST'])
@flask_login.login_required
def photoRecom():
	return render_template('photorecom.html', photos=getPhotoRecom(),base64=base64)


def isAlbumExist(a_id):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(albums_id) FROM Albums WHERE albums_id = '{0}' ".format(a_id))
	num = cursor.fetchall()
	if num == ((1,),):
		return True
	else:
		return False


def isAlbumBelong(aid, uid):
		#use this to check if a email has already been registered
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(albums_id) FROM Albums WHERE albums_id = '{0}' AND user_id = '{1}'".format(aid, uid))
	num = cursor.fetchall()
	if num == ((1,),):
		return True
	else:
		return False

#end photo uploading code

#ViewUserPhots
@app.route('/viewmyphotos', methods = ['Get'])
@flask_login.login_required

def viewmyphotos():
		uid = getUserIdFromEmail(flask_login.current_user.id)
		cursor = conn.cursor()
		cursor.execute("SELECT albums_id, name, date FROM albums WHERE user_id = '{0}'".format(uid))
		album = cursor.fetchall()
		return render_template('viewmyphotos.html', album1 = album)

@app.route('/viewmyalbum', methods = ['Post'])
def SearchBYID1():
	try:
		a_id =int(request.form.get('Album ID'))
	except:
		print("Please Enter Some THIng") 
		#this prints to shell, end users will not see this (all print statements go to shell)
		return render_template('hello.html', message = "Failed, invalid input")
		#return render_template('hello.html', photo_data=photo)
	if isAlbumExist(a_id):
		cursor = conn.cursor()
		cursor.execute("SELECT data, photo_id, caption FROM Photos WHERE albums_id = '{0}'".format(a_id))
		photo = cursor.fetchall()
		#print(a_id)
		#print(photo)
		return render_template('photoaid.html', photo_data=photo,base64=base64)
	else:
		print("Please Enter Some THIng") 
		#this prints to shell, end users will not see this (all print statements go to shell)
		return render_template('hello.html', message = "Failed, invalid input")
		#return render_template('hello.html')


#ViewAllAlbums
@app.route('/viewallalbum', methods = ['Get'])
def viewallalbum():
		cursor.execute("SELECT albums.albums_id, albums.name, albums.date, users.first_name FROM albums, users WHERE albums.user_id = users.user_id")
		album = cursor.fetchall()
		return render_template('viewallalbum.html', album2 = album)

@app.route('/viewallalbum', methods = ['Post', 'Get'])
def SearchBYID():
	try:
		a_id =int(request.form.get('Album ID'))
	except:
		print("Please Enter Some Thing") 
		#this prints to shell, end users will not see this (all print statements go to shell)
		return render_template('hello.html', message = "Failed, invalid input")
		#return render_template('hello.html', photo_data=photo)
	if isAlbumExist(a_id):
		cursor = conn.cursor()
		cursor.execute("SELECT data, photo_id, caption FROM Photos WHERE albums_id = '{0}'".format(a_id))
		photo = cursor.fetchall()
		return render_template('photoaid.html', photo_data=photo,base64=base64)
	else:
		print("Please Enter Some THIng") 
		#this prints to shell, end users will not see this (all print statements go to shell)
		return render_template('hello.html', message = "Failed, invalid input")
		#return render_template('hello.html')

@app.route('/createalbum', methods = ['Get','Post'])
@flask_login.login_required
def createalbum():
	if request.method == 'POST':	
		try:
			uid = getUserIdFromEmail(flask_login.current_user.id)
			print(1)
			name1 =request.form.get('album_name')
			print(1)
			birth_date=request.form.get('birth_date')
			print(1)
			cursor = conn.cursor()
			cursor.execute("INSERT INTO Albums (name, date, user_id) VALUE ('{0}', '{1}', '{2}')".format(name1, birth_date, uid))
			conn.commit()
			print(1)
			return flask.redirect(flask.url_for('viewmyphotos'))
		except:
			print("Please Enter Some Thing") 
			#this prints to shell, end users will not see this (all print statements go to shell)
			return render_template('hello.html', message = "Failed, invalid input")
	else:
		return render_template('createalbum.html')


@app.route('/deletealbum', methods = ['Get','Post'])
@flask_login.login_required
def deletealbum():
	if request.method == 'POST':	
		try:
			uid = getUserIdFromEmail(flask_login.current_user.id)
			print(1)
			name1 =int(request.form.get('AlbumID'))
			print(1)
			if isAlbumBelong(name1, uid):
				print("Album belongs to the user")
				cursor = conn.cursor()
				cursor.execute("DELETE FROM Albums WHERE Albums.albums_id = '{0}'".format(name1))
				conn.commit()
				print("Delete Album")
				cursor = conn.cursor()
				cursor.execute("DELETE FROM Photos WHERE Photos.albums_id = '{0}'".format(name1))
				conn.commit()
				print("Delete All photos in album")
				return flask.redirect(flask.url_for('viewmyphotos'))
			else:
				print("Album does not belongs to user")
				return render_template('hello.html', message = "Failed, the album doesn't seems to belongs to you")
		except:
			print("Please Enter Some Thing") 
			#this prints to shell, end users will not see this (all print statements go to shell)
			return render_template('hello.html', message = "Failed, invalid input")
	else:
		return render_template('deletealbum.html')

	

@app.route('/deletephoto', methods = ['Get','Post'])
@flask_login.login_required
def deletephoto():
	if request.method == 'POST':	
		try:
			uid = getUserIdFromEmail(flask_login.current_user.id)
			print(uid)
			name1 =int(request.form.get('PhotoID'))
			print(name1)
			cursor = conn.cursor()
			cursor.execute("DELETE FROM Photos WHERE Photos.photo_id = '{0}' AND Photos.user_id = '{1}'".format(name1, uid))
			conn.commit()
			print(1)
			return flask.redirect(flask.url_for('hello'))
		except:
			print("Enter Things Wrong") 
			#this prints to shell, end users will not see this (all print statements go to shell)
			return render_template('hello.html', message = "Failed, check if you have entered the correct Photo ID")
	else:
		return render_template('deletephoto.html')


@app.route('/aphotos', methods = ['Get'])
def allphoto():
		allphoto = getAllPhotos()
		print(1)
		return render_template('aphotos.html', photos = allphoto, base64 = base64)

def getAllPhotos():
	cursor = conn.cursor()
	cursor.execute("SELECT data, photo_id, caption FROM Photos")
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]




@app.route('/likephotos', methods = ['Get', 'Post'])
@flask_login.login_required
def likePhotos():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	p_id= request.form.get('like')
	if request.method == 'POST':
		if iflikedphoto(uid, p_id):
			print("You have already liked this photo.")
			return render_template('likephotos.html',likedlist = listlikedphoto(uid), photos = getAllPhotos(), base64 = base64)
			print(1)
		# like = request.form.get('likePhoto')
		else:
			cursor = conn.cursor()
			cursor.execute("INSERT INTO Likes(photo_id, user_id) VALUES ('{0}', '{1}')".format(p_id, uid))
			conn.commit()
			print("LIKED Successful")
		return render_template('likephotos.html',likedlist = listlikedphoto(uid), photos = getAllPhotos(), base64 = base64)
	else:
		return render_template('likephotos.html', likedlist = listlikedphoto(uid), photos = getAllPhotos(), base64 = base64)

def iflikedphoto(uid, sid):
	cursor = conn.cursor()
	cursor.execute("SELECT  COUNT(user_id) FROM Likes WHERE user_id = '{0}' AND photo_id = '{1}'".format(uid, sid))
	a = cursor.fetchall()
	if a == ((1,),):
		return True
	else:
		return False

def listlikedphoto(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT photo_id FROM Likes WHERE user_id = '{0}'".format(uid))
	a = cursor.fetchall()
	return a


@app.route("/commentphoto", methods = ['POST', 'GET'])
def comment():
	if request.method == 'POST':
		pid = int(request.form.get("photoid"))
		print("Comment: Get Photo ID Corret")
		c = request.form.get("commenting")
		print("Comment: Get comment Test Corret")
		try:
			uid = getUserIdFromEmail(flask_login.current_user.id)
			print("Comment: Get user ID Corret")
			if(checkselfcomment(uid, pid)):
				print("Comment: Self Photo Comment Prohibited")
				return render_template('hello.html', message = "Comment: Self Photo Comment Prohibited")
			else:
				today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
				cursor = conn.cursor()
				cursor.execute("INSERT INTO Comments (photo_id, user_id, text, date) VALUES ('{0}', '{1}', '{2}', '{3}')".format(pid, uid, c, today ))
				cursor.execute("UPDATE Users SET contribution = contribution + 1 WHERE user_id='{0}'".format(uid))
				conn.commit()
				print("Comment successfully")
				return render_template('hello.html', message = "Comment Successfully")
		except:
			print("Comment: Comment As a Guest")
			today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
			cursor = conn.cursor()
			cursor.execute("INSERT INTO Users (email, password, first_name, last_name, contribution) VALUES ('UUUU@AAA', 'test', 'Anonymous', 'User', '0')")
			conn.commit()
			
			cursor = conn.cursor()
			cursor.execute("INSERT INTO Comments (photo_id, user_id, text, date) VALUES ('{0}','{1}', '{2}', '{3}')".format(pid, getUserIdByEmail("UUUU@AAA"), c, today ))
			conn.commit()
			return render_template('hello.html', message = "Comment Successfully As An Anonymous User")
	else:
		return render_template('commentphoto.html', photos = getAllPhotos(), base64 = base64)

def checkselfcomment(uid, pid):
	cursor = conn.cursor()
	cursor.execute("SELECT  COUNT(user_id) FROM Photos WHERE user_id = '{0}' AND photo_id = '{1}'".format(uid, pid))
	a = cursor.fetchall()
	print(a)
	if a == ((1,),):
		print("IS self photo")
		return True
	else:
		print("NOT self photo")
		return False

def getUserIdByEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM users WHERE email = '{0}'".format(email))
	a = cursor.fetchall()
	print(a)
	return a[-1][0]



@app.route("/commentdisplay", methods = ['POST', 'GET'])
def findcomment():
	if request.method == 'POST':
		pid = int(request.form.get("photoid"))
		print("Display Comments: Get PhotoID info")
		try:
			cursor = conn.cursor()
			cursor.execute("SELECT first_name, last_name, text FROM users U NATURAL JOIN (SELECT * FROM comments C WHERE C.photo_id = '{0}') AS CC;".format(pid))
			a = cursor.fetchall()
			print("Display Comments: Get Comment info")
			print(a)
			return render_template('commentdisplay.html', photos = findphoto(pid) , base64 = base64, comments = a)
		except:

			return render_template('hello.html', message = "Failed")
	else:
		return render_template("commentdisplay.html")


def findphoto(pid):
		cursor = conn.cursor()
		cursor.execute("SELECT data, photo_id, caption FROM Photos WHERE photo_id = '{0}'".format(pid))
		return cursor.fetchall()


@app.route("/searchcomment", methods = ["GET", "POST"])
def searchcomment():
	if request.method == "POST":
		try:
			t = request.form.get("commenttext")
			if cfind(t):
				cursor = conn.cursor()
				cursor.execute("SELECT C.user_id, COUNT(*) AS ccount, U.first_name, U.last_name, U.user_id  FROM Comments C, Users U WHERE text='{0}' AND C.user_id = U.user_id GROUP BY C.user_id ORDER BY ccount DESC".format(t))
				print("sql conduct")
				l = cursor.fetchall()
				
				return render_template("searchcomment.html", comments = t, list = l)
			else:
				return render_template("searchcomment,html", res = " ")
		except:
			return render_template("hello.html", message = "Failed")
	else:
		return render_template("searchcomment.html")

def cfind(t):
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(user_id) FROM comments WHERE text = '{0}'".format(t))
	a = cursor.fetchall()
	if a == ((0,),):
		print("NO comment find")
		return False
	else:
		print("Find Comment")
		return True

#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welecome to Photoshare', topContribute = getTopContribute(), topTag = getTopTag())

if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
