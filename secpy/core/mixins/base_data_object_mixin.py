import json


class BaseDataObjectMixin:
    def to_json(self):
        """
        Converts object to JSON dict
        @return: dict
        """
        return json.dumps(self, default=lambda o: o.__dict__)
