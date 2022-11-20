#!/usr/bin/python3
"""Cities view for the Flask API"""

from flask import jsonify, request
from api.v1.views import app_views
from models import storage, storage_t
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest


METHODS_ALLOWED = ["GET", "POST", "PUT", "DELETE"]


@app_views.route('/states/<state_id>/cities', methods=['GET', 'POST'])
@app_views.route('/cities/<city_id>', methods=['GET', 'DELETE', 'PUT'])
def handle_cities(state_id=None):
    '''This method handles the cities endpoint.
    '''
    handlers = {
        'GET': get_cities,
        'DELETE': remove_city,
        'POST': add_city,
        'PUT': city_update,
    }
    if request.method in handlers:
        return handlers[request.method](state_id)
    else:
        raise MethodNotAllowed(list(handlers.keys()))


def get_cities(state_id=None, city_id=None):
    '''Retrieves the city with the given id otherwise, all cities
    in a state.
    '''
    if state_id:
        state = storage.get(State, state_id)
        if state:
            cities = list(map(lambda x: x.to_dict(), state.cities))
            return jsonify(cities)
    elif city_id:
        city = storage.get(City, city_id)
        if city:
            return jsonify(city.to_dict())
    raise NotFound()


def remove_city(state_id=None, city_id=None):
    '''Removes a state using the given id.
    '''
    if city_id:
        city = storage.get(City, city_id)
        if city:
            storage.delete(city)
            if storage_t != "db":
                for place in storage.all(Place).values():
                    if place.city_id == city_id:
                        for review in storage.all(Review).values():
                            if review.place_id == place.id:
                                storage.delete(review)
                        storage.delete(place)
            storage.save()
            return jsonify({}), 200
    raise NotFound()


def add_city(state_id=None):
    '''Adds a new state to the storage.
    '''
    state = storage.get(State, state_id)
    if not state:
        raise NotFound()
    data = request.get_json()
    if type(data) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'name' not in data:
        raise BadRequest(description='Missing name')
    data['state_id'] = state_id
    city = City(**data)
    city.save()
    return jsonify(city.to_dict()), 201


def city_update(state_id=None, city_id=None):
    '''Updates the city using the given id.
    '''
    dict_keys = ('id', 'state_id', 'created_at', 'updated_at')
    if city_id:
        city = storage.get(City, city_id)
        if city:
            data = request.get_json()
            if type(data) is not dict:
                raise BadRequest(description='Not a JSON')
            for key, value in data.items():
                if key not in dict_keys:
                    setattr(city, key, value)
            city.save()
            return jsonify(city.to_dict()), 200
    raise NotFound()
