from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Items, Rooms, Users
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///householdinventory.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def createNewUser(login_session):
    newUser = Users(name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(Users).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(Users).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(Users).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    secrets_f = open('fb_client_secrets.json', 'r')
    secrets = json.loads(secrets_f.read())
    app_id = secrets['web']['app_id']
    app_secret = secrets['web']['app_secret']
    url = "https://graph.facebook.com/oauth/toaken?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s&redirect_uri=http://localhost:5000" % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print result

    userinfo_url = "https://graph.facebook.com/v2.4/me?&redirect_uri=http://localhost:5000"
    token = result.split("&")[0]
    print token

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print result

    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    url = 'https://graph.facebook.com/v2.6/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createNewUser(login_session)
    login_session['user_id'] = user_id

    # output = ''
    # output += '<h1>Welcome, '
    # output += login_session['username']
    # output += '!</h1>'
    # output += '<img src="'
    # output += login_session['picture']
    # output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    # flash("you are now logged in as %s" % login_session['username'])
    # print "done!"
    # return output
    flash("Now logged in as %s." % login_session['username'])
    return redirect('/')


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['facebook_id']
    return "You have been logged out"


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash('You have been logged out!')
        return redirect(url_for('listRooms'))


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template("login.html", STATE=state)


@app.route('/owners')
def listOwners():
    owners = session.query(Users).all()
    return render_template("owners.html",
                           owners=owners)


@app.route('/owners/<int:owner_id>')
def showOwner(owner_id):
    owner = session.query(Users).filter_by(id=owner_id).one()
    items = session.query(Items).filter_by(user_id=owner.id).all()
    return render_template("owner.html",
                           owner=owner,
                           items=items)


@app.route('/')
@app.route('/items')
@app.route('/rooms')
def listRooms():
    rooms = session.query(Rooms).all()
    return render_template("rooms.html", rooms=rooms)


@app.route('/rooms/JSON')
def listRoomsJSON():
    rooms = session.query(Rooms).all()
    return jsonify(Rooms=[r.serialize for r in rooms])


@app.route('/rooms/new', methods=['GET', 'POST'])
def newRoom():
    if request.method == 'GET':
        return render_template("newRoom.html")
    elif request.method == 'POST':
        newRoom = Rooms(name=request.form['name'])
        session.add(newRoom)
        session.commit()
        flash("Room added!")
        return redirect(url_for('listRooms'))


@app.route('/rooms/<int:room_id>/edit', methods=['GET', 'POST'])
def editRoom(room_id):
    room = session.query(Rooms).filter_by(id=room_id).one()
    if request.method == 'GET':
        return render_template("editRoom.html",
                               room=room)
    elif request.method == 'POST':
        room.name = request.form['name']
        session.add(room)
        session.commit()
        flash("Room name changed!")
        return redirect(url_for('listRooms'))


@app.route('/rooms/<int:room_id>/delete', methods=['GET', 'POST'])
def deleteRoom(room_id):
    room = session.query(Rooms).filter_by(id=room_id).one()
    if request.method == 'GET':
        return render_template("deleteRoom.html",
                               room=room)
    elif request.method == 'POST':
        items = session.query(Items).filter_by(room_id=room.id).all()
        session.delete(room)
        for item in items:
            session.delete(item)
        session.commit()
        flash("Room and all contents deleted!")
        return redirect(url_for('listRooms'))


@app.route('/rooms/<int:room_id>')
def showRoom(room_id):
    room = session.query(Rooms).filter_by(id=room_id).one()
    items = session.query(Items).filter_by(room_id=room_id).all()
    return render_template("room.html",
                           room=room,
                           items=items)


@app.route('/rooms/<int:room_id>/JSON')
def showRoomJSON(room_id):
    items = session.query(Items).filter_by(room_id=room_id).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/items/new', methods=['GET', 'POST'])
def newItem():
    if request.method == 'GET':
        owners = session.query(Users).all()
        rooms = session.query(Rooms).all()
        return render_template("newItem.html",
                               owners=owners,
                               rooms=rooms)
    if request.method == 'POST':
        room_id = request.form['room']
        newItem = Items(name=request.form['name'],
                        user_id=request.form['owner'],
                        room_id=room_id,
                        value=request.form['value'],
                        description=request.form['description'])
        session.add(newItem)
        session.commit()
        flash("Item added!")
        return redirect(url_for('showRoom', room_id=room_id))


@app.route('/items/JSON')
def showItemsJSON():
    items = session.query(Items).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):
    item = session.query(Items).filter_by(id=item_id).one()
    if request.method == 'GET':
        rooms = session.query(Rooms).all()
        return render_template('editItem.html',
                               item=item,
                               rooms=rooms)
    if request.method == 'POST':
        if request.form['room']:
            room_id = request.form['room']
            item.room_id = room_id
        else:
            room_id = item.room_id

        if request.form['name']:
            item.name = request.form['name']
        if request.form['value']:
            item.value = request.form['value']
        if request.form['description']:
            item.description = request.form['description']
        session.add(item)
        session.commit()
        flash("Item updated!")
        return redirect(url_for('showRoom', room_id=room_id))


@app.route('/items/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(item_id):
    item = session.query(Items).filter_by(id=item_id).one()
    if request.method == 'GET':
        return render_template('deleteItem.html',
                               item=item)
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Item has been deleted!")


@app.route('/items/<int:item_id>')
def showItem(item_id):
    item = session.query(Items).filter_by(id=item_id).one()
    owner = session.query(Users).filter_by(id=item.user_id).one()
    room = session.query(Rooms).filter_by(id=item.room_id).one()
    return render_template("item.html",
                           item=item,
                           owner=owner,
                           room=room)


@app.route('/items/<int:item_id>/JSON')
def showItemJSON(item_id):
    item = session.query(Items).filter_by(id=item_id).one()
    return jsonify(Items=[item.serialize])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
