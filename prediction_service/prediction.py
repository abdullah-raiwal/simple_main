import yaml
import os
import json
import joblib
import numpy as np

params_path = "params.yaml"
schema_path = os.path.join("prediction_service", "schema.json")


class NotinRange(Exception):
    def __init__(self, message="value not in range"):
        self.message = message
        super().__init__(self.message)


class NotinColumn(Exception):
    def __init__(self, message="value not in column"):
        self.message = message
        super().__init__(self.message)


def read_params(config_path):
    with open(config_path) as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config


def predict(data):
    config = read_params(params_path)
    model_dir = config["webapp_model_dir"]
    model = joblib.load(model_dir)
    prediction = model.predict(data)

    try:
        if 3 <= prediction <= 8:
            return prediction
        else:
            raise NotinRange
    except NotinRange:
        return "Unexpected error"


def get_schema(schema_path=schema_path):
    with open(schema_path) as json_file:
        config = json.load(json_file)
    return config


def validation(dict_data):
    def _validate_cols(cols):
        schema = get_schema()
        actual_cols = schema.keys()
        if cols not in actual_cols:
            raise NotinColumn

    def _validate_values(col, val):
        schema = get_schema()
        if not (float(schema[col]["min"]) <= float(dict_data[col]) <= float(schema[col]["max"])):
            raise NotinRange

    for col, val in dict_data.items():
        _validate_cols(col)
        _validate_values(col, val)

    return True


def form_response(dict_data):
    for col in dict_data.keys():
        dict_data[col] = float(dict_data[col])

    print("in form response")
    print(dict_data)

    if validation(dict_data):
        data = [dict_data.get(key) for key in dict_data.keys()]
        data = [list(map(float, data))]
        print("validation complete")
        response = predict(data)
        return response[0]


def api_response(dict_data):
    try:
        if validation(dict_data):
            data = np.array([list(dict_data.values())])
            response = predict(data)
            response = {'response': response}
            return response
    except Exception as e:
        response = {"the_expected_range": get_schema(),
                    "response": str(e)}
        return response
