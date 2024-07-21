# Example usage with Flask
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from schema.json import RootSchema, ModelResualt
from utils.parser import (
    convert_json_schema_to_model_data,
    convert_model_resualt_to_json,
)
from solver.solver import ModelSolver, parse_courses, TimeProf

app = Flask(__name__)
cors = CORS(app)


@cross_origin()
@app.route("/api/calc", methods=["POST"])
def parse_json():
    try:
        # Parse and validate the JSON using Pydantic
        json_data = request.json
        if not json_data:
            return jsonify({})
        parsed_data = RootSchema(**json_data)
        data = convert_json_schema_to_model_data(parsed_data)
        number_solution = (
            parsed_data.settings["number_solution"]
            if "number_solution" in parsed_data.settings
            else 20
        )
        Mo = ModelSolver(data=parse_courses(data), num_solution=number_solution)
        sols: list[list[tuple[str, TimeProf,int]]] = Mo.solve()
        resualt=convert_model_resualt_to_json(sols=sols, parsed_json_data=parsed_data)
        response = {
            "message": "JSON data successfully parsed and validated",
            "data": resualt.model_dump(),
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
