from models import db
from flask import request, jsonify, make_response
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from models import UserModel

class UsersView(Resource):
    def get(self):
        users = UserModel.query.all()
        return {'users': [user.json() for user in users]}

    def post(self):
        def check_data(data): return True if len(data) > 0 else False
        status_code = 400
        message = {'error': 'json data expected'}

        if request.is_json:
            # get data in json format
            data = dict(request.get_json())

            # extract variables
            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            email = data.get('email', '').strip()
        else:
            # extract variables
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip()

        # check if user already exists
        user_present = True
        if UserModel.query.filter_by(email=email).first() is None:
            user_present = False
        else:
            message = {'message': 'email already used'}
            
        # validate data and if user is not present then
        # create and store new user 
        if check_data(first_name) and check_data(last_name) and check_data(email) and not user_present:
            new_user = UserModel(
                first_name=first_name,
                last_name=last_name,
                email=email,
                jwt_token=create_access_token(identity=email)
            )
            db.session.add(new_user)
            db.session.commit()
            message = new_user.json(hide_sensitive_info=False)
            status_code = 201

        return make_response(jsonify(message), status_code)