# Example usage with Flask
from flask import Flask, request, jsonify
from schema.json import RootSchema
from utils.parser import json_parser

app = Flask(__name__)


@app.route("/api/calc", methods=["POST"])
def parse_json():
    try:
        # Parse and validate the JSON using Pydantic
        json_data = request.json
        parsed_data = RootSchema(**json_data)
        json_parser(parsed_data)
        response = {
            "message": "JSON data successfully parsed and validated",
            "data": json_parser(parsed_data),
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
