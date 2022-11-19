#!/usr/bin/python3
"""States view for the Flask API"""

from flask import jsonify, request
from api.v1.views import app_views
from models import storage
from models.state import State
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest


METHODS_ALLOWED = ["GET", "POST", "PUT", "DELETE"]


@app_views.route('/states', methods=METHODS_ALLOWED)
@app_views.route('/states/<state_id>', methods=METHODS_ALLOWED)
def handle_states(state_id=None):
    '''The method handler for the states endpoint.
    '''
    handlers = {
        'GET': get_states,
        'DELETE': remove_state,
        'POST': add_state,
        'PUT': state_update,
    }
    if request.method in handlers:
        return handlers[request.method](state_id)
    else:
        raise MethodNotAllowed(list(handlers.keys()))


def get_states(state_id=None):
    '''Retrieves the state with the given id otherwise, all states.
    '''
    all_states = storage.all(State).values()
    if state_id:
        result = list(filter(lambda x: x.id == state_id, all_states))
        if result:
            return jsonify(result[0].to_dict())
        raise NotFound()
    all_states = list(map(lambda x: x.to_dict(), all_states))
    return jsonify(all_states)


def remove_state(state_id=None):
    '''Removes a state using the given id.
    '''
    all_states = storage.all(State).values()
    result = list(filter(lambda x: x.id == state_id, all_states))
    if result:
        storage.delete(result[0])
        storage.save()
        return jsonify({}), 200
    raise NotFound()


def add_state(state_id=None):
    '''Adds a new state to the storage.
    '''
    data = request.get_json()
    if type(data) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'name' not in data:
        raise BadRequest(description='Missing name')
    new_state = State(**data)
    new_state.save()
    return jsonify(new_state.to_dict()), 201


def state_update(state_id=None):
    '''Updates the state using the given id.
    '''
    dict_keys = ('id', 'created_at', 'updated_at')
    all_states = storage.all(State).values()
    result = list(filter(lambda x: x.id == state_id, all_states))
    if result:
        data = request.get_json()
        if type(data) is not dict:
            raise BadRequest(description='Not a JSON')
        old_state_data = result[0]
        for key, value in data.items():
            if key not in dict_keys:
                setattr(old_state_data, key, value)
        old_state_data.save()
        return jsonify(old_state_data.to_dict()), 200
    raise NotFound()
