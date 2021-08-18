def to_json(obj):
    ret = {}
    for key, value in obj.__dict__.items():
        if value is not None:
            if isinstance(value, (str, bool, float, int)):
                ret[key] = value
            elif isinstance(value, list):
                ret[key] = [to_json(item) for item in value]

            else:
                ret[key] = value.to_json()
        else:
            ret[key] = value

    return ret


class JsonSerializable:
    def to_json(self):
        return to_json(self)
