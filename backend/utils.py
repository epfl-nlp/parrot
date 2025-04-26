from uuid import uuid4


def generate_uuid():
    return str(uuid4())

def clean_string(s):
    if s is None:
        return None
    return s.replace("\x00", "")