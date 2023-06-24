"""
By Dmitry Kotov t.me/wavecat
"""

import json
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class Param:
    type: type
    description: str
    enum: list[object] = None
    required: bool = True


types = {
    "str": "string",
    "int": "integer"
}


class Functions:
    functions = {}

    def __call__(self, function: Callable):
        self.functions[function.__name__] = function
        return function

    def to_json(self):
        result = []

        for function_name, function in self.functions.items():
            args = function.__annotations__.copy()

            properties = {}
            result.append({
                "name": function_name,
                "description": function.__doc__,
                "parameters": {
                    "type": "object",
                    "properties": properties
                },
                "required": []
            })

            for name, arg in args.items():
                if isinstance(arg, Param):
                    properties[name] = {
                        "type": types.get(arg.type.__name__, "string")
                    }

                    if arg.description:
                        properties[name]["description"] = arg.description

                    if arg.enum:
                        properties[name]["enum"] = arg.enum

                    if arg.required:
                        result[-1]["required"].append(name)

        return result

    def call_functions(self, message: dict) -> Optional[dict]:
        function_call = message.get("function_call")

        if function_call:
            function_name = function_call["name"]

            if self.functions.get(function_name):
                function = self.functions[function_name]

                arguments = json.loads(function_call["arguments"])

                call_args = {}
                for name in function.__annotations__.keys():
                    arg = arguments.get(name)
                    if arg:
                        call_args[name] = arg

                result = function(**call_args)

                return {
                    "role": "function",
                    "name": function_name,
                    "content": str(result),
                }

        return None
