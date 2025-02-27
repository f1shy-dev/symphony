import os
import json
from pydantic import BaseModel
from typing import Any, Callable, Type
import sys

sys.path.insert(0, os.path.abspath('functions'))


def remove_title(schema):
    if 'title' in schema:
        schema.pop('title')

    for value in schema.values():
        if isinstance(value, dict):
            remove_title(value)


def generate_function_description(name, function: Callable[..., Any], request_model: Type[BaseModel], response_model: Type[BaseModel]) -> dict:
    request_schema = request_model.model_json_schema()
    response_schema = response_model.model_json_schema()

    remove_title(request_schema)
    # remove_title(response_schema)

    request_schema = {'type': request_schema['type'], **request_schema}
    # response_schema = {'type': response_schema['type'], **response_schema}

    function_description = {
        "name": name,
        "description": function.__doc__.strip(),
        "parameters": request_schema,
        # "returns": response_schema,
    }

    return function_description


def main(directory):
    descriptions = []

    for filename in os.listdir(directory):
        if filename.endswith('.py'):
            module_name = filename[:-3]
            module = __import__(f'{module_name}')
            function = getattr(module, 'handler')
            symphony_request = getattr(module, 'SymphonyRequest')
            symphony_response = getattr(module, 'SymphonyResponse')
            fn_name = module_name + '-py'
            description = generate_function_description(
                fn_name, function, symphony_request, symphony_response)
            descriptions.append(description)

    with open('./server/python/descriptions.json', 'w') as f:
        json.dump(descriptions, f, indent=4)


if __name__ == '__main__':
    directory = 'functions'
    main(directory)
