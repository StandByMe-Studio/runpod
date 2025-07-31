import base64


def bytes_to_b64(bt):
  return base64.b64encode(bt).decode('utf-8')


def b64_to_bytes(b64):
  return base64.b64decode(b64)