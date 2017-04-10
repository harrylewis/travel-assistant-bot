#!bin/python

from flask import (Flask, jsonify, abort, make_response)

import api

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "country_advisory": "http://localhost:5000/api/1/advisory/{country}"
    })


@app.route("/api/1/advisory/<string:country>", methods=["GET"])
def get_advisory_country(country):
    """

    :param country:
    :return:
    """
    country_data = api.advisory_country(country.lower())

    if not bool(country_data):
        abort(404)

    return jsonify(country_data)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not Found"}), 404)


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()