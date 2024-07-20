# Example usage with Flask
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from schema.json import RootSchema, ModelResualt, ResualtCourse
from utils.parser import convert_json_schema_to_model_data
from solver.solver import ModelSolver, parse_courses, TimeProf, minutes_to_time

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
            else 100
        )
        Mo = ModelSolver(data=parse_courses(data), num_solution=number_solution)
        sols: list[list[tuple[int, TimeProf]]] = Mo.solve()
        resualt = ModelResualt(resualts=list(list()))
        for i in sols:
            sol_coruses = list()
            for id, timeslot in i:
                for course in parsed_data.data.courses:
                    if not course.id == id:
                        continue
                    resualt_course = ResualtCourse(
                        id=id,
                        name=course.name,
                        units=course.units,
                        duration=course.duration,
                        semister=int(timeslot.group),
                        day=int(timeslot.day),
                        start=str(minutes_to_time(timeslot.start)),
                        end=str(minutes_to_time(timeslot.end)),
                        professor_id=int(timeslot.prof),
                        is_prefered_time=bool(timeslot.prefered),
                    )
                    sol_coruses.append(resualt_course)
            resualt.resualts.append(sol_coruses)
        response = {
            "message": "JSON data successfully parsed and validated",
            "data": resualt.model_dump(),
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
