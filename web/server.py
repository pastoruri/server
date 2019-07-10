from flask import Flask, render_template, request, session, Response, redirect
from web.database import connector
from web.model import entities
import json
import time

db = connector.Manager()
engine = db.createEngine()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<content>')
def static_content(content):
    return render_template(content)


@app.route('/users', methods=['GET'])
def get_users():
    db_session = db.getSession(engine)
    users = db_session.query(entities.User)
    data = []
    for user in users:
        data.append(user)
    message = {'contacts': data}
    return Response(json.dumps(message, cls=connector.AlchemyEncoder), mimetype='application/json')


@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    db_session = db.getSession(engine)
    users = db_session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return Response(js, status=200, mimetype='application/json')

    message = { 'status': 404, 'message': 'Not Found'}
    return Response(message, status=404, mimetype='application/json')

@app.route('/create_test_users', methods = ['GET'])
def create_test_users():
    db_session = db.getSession(engine)
    user = entities.User(name="David", fullname="Lazo", password="1234", username="qwerty")
    db_session.add(user)
    db_session.commit()
    return "Test user created!"

@app.route('/users', methods = ['DELETE'])
def delete_message():
    id = request.form['key']
    session = db.getSession(engine)
    messages = session.query(entities.User).filter(entities.User.id == id)
    for message in messages:
        session.delete(message)
    session.commit()
    return "Deleted user!"

@app.route('/users', methods = ['POST'])
def create_user():
    c = json.loads(request.form['values'])
    user = entities.User(
        username=c['username'],
        name=c['name'],
        fullname=c['fullname'],
        password=c['password']
    )
    db_session = db.getSession(engine)
    db_session.add(user)
    db_session.commit()
    return 'Created User'

@app.route('/authenticate', methods=["POST"]) # TODO
def authenticate():
    message = json.loads(request.data)
    username = message['username']
    password = message['password']
    #2. look in database
    db_session = db.getSession(engine)
    try:
        user = db_session.query(entities.User).filter(entities.User.username == username).filter(entities.User.password == password).one()
        session['logged_user'] = user.id
        # looking for all users
        user_contacts = db_session.query(entities.User).filter(entities.User.id != user.id).all()
        contacts = []
        for u in user_contacts:
            contacts.append(u.username)
        # looking for all users
        message = {'message': 'Authorized', 'username': user.username, 'contacts': contacts, 'user_id': user.id}
        return Response(json.dumps(message, cls=connector.AlchemyEncoder), status=200, mimetype='application/json')
    except Exception:
        message = {'message': 'Unauthorized'}
        return Response(json.dumps(message, cls=connector.AlchemyEncoder), status=401, mimetype='application/json')

@app.route('/current', methods = ["GET"])
def current_user():
    db_session = db.getSession(engine)
    user = db_session.query(entities.User).filter(
        entities.User.id == session['logged_user']
        ).first()
    return Response(json.dumps(
            user,
            cls=connector.AlchemyEncoder),
            mimetype='application/json'
        )

@app.route('/logout', methods = ['GET'])
def logout():
    session.clear()
    return render_template('index.html')


@app.route('/messages/<user_from_id>/<user_to_id>', methods=['GET']) # returns an array of all messages from 'user_from' to 'user_to' and viceversa
def get_messages(user_from_id, user_to_id):
    db_session = db.getSession(engine)
    # All messages from user_from to user_to and viceversa
    messages = db_session.query(entities.Message).filter(entities.Message.user_from_id == user_from_id).filter(entities.Message.user_to_id == user_to_id).all()
    more_messages = db_session.query(entities.Message).filter(entities.Message.user_from_id == user_to_id).filter(entities.Message.user_to_id == user_from_id).all()
    messages = more_messages + messages

    data = []
    for message in messages:
        data.append(message)

    mensajes = {'messages': data}
    return Response(json.dumps(mensajes, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/gabriel/messages', methods = ["POST"]) # creates message and adds it to database
def create_message():
    data = json.loads(request.data)
    user_to_id = data['user_to_id']
    user_from_id = data['user_from_id']
    content = data['content']

    message = entities.Message(user_to_id=user_to_id, user_from_id=user_from_id, content=content)

    #2. Save in database
    db_session = db.getSession(engine)
    db_session.add(message) # add message to database
    db_session.commit()

    message = {'content': True}

    return Response(json.dumps(message, cls=connector.AlchemyEncoder), status=200, mimetype='application/json')  # returns the message content

@app.route('/messages/<user_from_id>/<user_to_id>', methods=['DELETE'])
def delete_messages(user_from_id, user_to_id):
    db_session = db.getSession(engine)
    messages = db_session.query(entities.Message).filter(entities.Message.user_from_id == user_from_id).filter(entities.Message.user_to_id == user_to_id)
    for message in messages:
        db_session.delete(message)
    db_session.commit()
    response = {'status': 'deleted'}

    return Response(json.dumps(response, cls=connector.AlchemyEncoder), mimetype='application/json')

##### PROYECTO MOBILE #####

@app.route('/create_commands', methods=['GET'])
def create_commands():
    db_session = db.getSession(engine)
    command = entities.Command(name="cal", description="cal shows the calendar of the current month and highlights the current day.")
    db_session.add(command)
    db_session.commit()
    return "Test command created " + command.name + "  " + command.description

@app.route('/commands', methods=['GET'])
def get_commands():
    dbSession = db.getSession(engine)
    commands = dbSession.query(entities.Command).all()

    data = []
    for command in commands:
        data.append(command)

    response = {'commands': data}
    return Response(json.dumps(response, cls=connector.AlchemyEncoder), status=200, mimetype='application/json')

@app.route('/commands', methods=['POST'])
def create_command():
    data = json.loads(request.data)
    name = data['name']
    description = data['description']

    command = entities.Command(name=name, description=description)

    dbSession = db.getSession(engine)
    dbSession.add(command)
    dbSession.commit()

    message = {'posted': True}

    return Response(json.dumps(message, cls=connector.AlchemyEncoder), status=200, mimetype='application/json')

@app.route('/commands/<id>', methods=['DELETE'])
def delete_command(id):
    dbSession = db.getSession(engine)
    command = dbSession.query(entities.Command).filter(entities.Command.id == id).one()
    dbSession.delete(command)
    dbSession.commit()

    message = {'deleted': True}

    return Response(json.dumps(message, cls=connector.AlchemyEncoder), status=200, mimetype='application/json')

if __name__ == '__main__':
    app.secret_key = ".."
    app.run(port=8080, threaded=True, host='127.0.0.1')
