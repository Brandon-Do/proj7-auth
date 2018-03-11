# Laptop Service

from flask import Flask, request, session
from flask_restful import Resource, Api
from pymongo import MongoClient
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
import json
import random
import pymongo
import csv
import time
import os

# Instantiate the app
app = Flask(__name__)
client = MongoClient("db", 27017)
db = client.tododb
cred_db = client.cred_db
api = Api(app)
DEFAULT_TOP = -1 #Any negative integer => limitless

                            ###################
                            ### API SERVICE ###
                            ###################

def retrieve_json(top = DEFAULT_TOP, fields = ["km", "open", "close"]):
    """
        The data within the MongoDB is structured to have fields 'km', 'open', 'close'.
        Pass this function a list of fields that are wanted, returns dictionary with corresponding fields.
    """

    if verify_auth_token(session['token']):
        data = db.tododb.find().sort("open", pymongo.ASCENDING)
        results = {}
        for field in fields:
            results[field] = []
        for d in data:
            if top == 0:
                break
            top -= 1
            for field in fields:
                results[field].append(d[field])
        return results, 200

    else:
        return "UNAUTHORIZED", 401

def retrieve_csv(top = DEFAULT_TOP, fields = ["km", "open", "close"]):
    """
        The data within the MongoDB is structured to have fields 'km', 'open', 'close'.
        Pass this function a list of fields that are wanted, returns dictionary with corresponding fields.
    """
    if verify_auth_token(session['token']):
        data = db.tododb.find().sort("open", pymongo.ASCENDING)
        results = ""
        for field in fields:
            results += field + ","
        results  += os.linesep
        for d in data:
            if top == 0:
                break
            top -= 1
            for field in fields:
                results += d[field] + ","
            results  += os.linesep
        return results.strip(os.linesep), 200

    else:
        return "UNAUTHORIZED", 401

def handle(arg_str):
    if arg_str == None or not arg_str.isdigit():
        global DEFAULT_TOP
        top = DEFAULT_TOP
    else:
        top = int(arg_str)
    return top


class listAll(Resource):
    def get(self):
        top = handle(request.args.get("top"))
        return retrieve_json(top)


class listAll_json(Resource):
    def get(self):
        top = handle(request.args.get("top"))
        return retrieve_json(top)


class listAll_csv(Resource):
    def get(self):
        top = handle(request.args.get("top"))
        return retrieve_csv(top)


class listOpen(Resource):
    def get(self):
        top = handle(request.args.get("top"))
        return retrieve_json(top, ["open"])


class listOpen_json(Resource):
    def get(self):
        top = handle(request.args.get("top"))
        return retrieve_json(top, ["open"])


class listOpen_csv(Resource):
    def get(self):
        top = handle(request.args.get("top"))
        return retrieve_csv(top, ["open"])


class listClose(Resource):
    def get(self):
        top = handle(request.args.get("top"))
        return retrieve_json(top, ["close"])


class listClose_json(Resource):
    def get(self):
        top = handle(request.args.get("top"))
        return retrieve_json(top, ["close"])

class listClose_csv(Resource):
    def get(self):
        top = handle(request.args.get("top"))
        return retrieve_csv(top, ["close"])


api.add_resource(listAll, '/listAll')
api.add_resource(listAll_json, '/listAll/json')
api.add_resource(listAll_csv, '/listAll/csv')

api.add_resource(listOpen, '/listOpenOnly')
api.add_resource(listOpen_json, '/listOpenOnly/json')
api.add_resource(listOpen_csv, '/listOpenOnly/csv')

api.add_resource(listClose, '/listCloseOnly')
api.add_resource(listClose_json, '/listCloseOnly/json')
api.add_resource(listClose_csv, '/listCloseOnly/csv')

                        #####################
                        ### AUTHORIZATION ###
                        #####################

app.config['SECRET_KEY'] = 'No one can actually see my secret key right'


def hash_password(password):
    return pwd_context.encrypt(password)

def verify_password(password, hashVal):
    return pwd_context.verify(password, hashVal)

def generate_auth_token(profile_id, expiration=60 * 10):
   s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
   return s.dumps({'profile_id': profile_id})

def verify_auth_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        return False    # valid token, but expired
    except BadSignature:
        return False    # invalid token
    return True


class register_user(Resource):
    """
    Creates a user profile and then stores into MongoDB
    """
    def get(self):
        try:
            profile_id = random.randint(10000000, 99999999)
            app.logger.debug(profile_id)
            username = request.args.get("username")
            password = hash_password(request.args.get("password"))

            data = db.cred_db.find({"username":username})
            for d in data:
                existing_username = d["username"]
                if existing_username == username:
                    return "USERNAME EXISTS", 401

            result = db.cred_db.insert({"username":username, "password":password, "profile_id":profile_id})
            return "SUCCESSFULLY REGISTERED", 200

        except:
            return "ERROR", 400


class get_token(Resource):
    """
    Verify's that the user credentials, and then sends token dependent on if the credentials are valid.
    """
    def get(self):
        try:
            user_in = request.args.get("username")
            pass_in = request.args.get("password")

            data = db.cred_db.find({"username":user_in})
            for d in data:
                password = d["password"]
                if verify_password(pass_in, password):
                    session['token'] = generate_auth_token(d["profile_id"])
                    return "SUCCESS", 200

            return "INCORRECT USERNAME AND PASSWORD COMBINATION", 400                       # Couldn't find the
        except:
            return "BAD REQUEST", 400


# class display_db(Resource):
#     def get(self):
#         # db.cred_db.delete_many({})
#         # Debugging purposes only:
#         fields = ["username", "password", "profile_id"]
#         data = db.cred_db.find()
#         results = {}
#         for field in fields:
#             results[field] = []
#         for d in data:
#             for field in fields:
#                     results[field].append(d[field])
#
#         return results
#api.add_resource(display_db, '/api/display')   #For Debugging


api.add_resource(register_user, '/api/register')
api.add_resource(get_token, '/api/token')

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
