import websocket
import uuid
import json, base64
import urllib.request
import urllib.parse
import runpod


server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

def queue_prompt(prompt, prompt_id):
  p = {"prompt": prompt, "client_id": client_id, "prompt_id": prompt_id}
  data = json.dumps(p).encode('utf-8')
  req = urllib.request.Request("http://{}/prompt".format(server_address), data=data)
  urllib.request.urlopen(req).read()

def get_image(filename, subfolder, folder_type):
  data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
  url_values = urllib.parse.urlencode(data)
  with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
    return response.read()

def get_history(prompt_id):
  with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
    return json.loads(response.read())

def get_images(ws, prompt):
  prompt_id = str(uuid.uuid4())
  queue_prompt(prompt, prompt_id)
  output_images = {}
  while True:
    out = ws.recv()
    if isinstance(out, str):
      message = json.loads(out)
      if message['type'] == 'executing':
        data = message['data']
        if data['node'] is None and data['prompt_id'] == prompt_id:
          break #Execution is done
    else:
      # If you want to be able to decode the binary stream for latent previews, here is how you can do it:
      # bytesIO = BytesIO(out[8:])
      # preview_image = Image.open(bytesIO) # This is your preview in PIL image format, store it in a global
      continue #previews are binary data

  history = get_history(prompt_id)[prompt_id]
  print('history', len(history['outputs']))
  for node_id in history['outputs']:
    node_output = history['outputs'][node_id]
    print('node_id', node_id, 'node_output', node_output)
    images_output = []
    if 'images' in node_output:
      for image in node_output['images']:
        image_data = get_image(image['filename'], image['subfolder'], image['type'])
        images_output.append(image_data)
    output_images[node_id] = images_output

  print('output_images', output_images)

  return output_images


def handler(job):
  input = job['input']
  if input['prompt_id'] == 'sample':
    filename = 'src/prompt_sample.json'
  elif input['prompt_id'] == 'mp4':
    filename = 'src/prompt_mp4.json'
  else:
    return {'error': 'Invalid prompt id'}
  with open(filename, 'r', encoding='utf-8') as f:
    prompt = json.load(f)
  ws = websocket.WebSocket()
  ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
  images = get_images(ws, prompt)
  ws.close()

  data = images['9'][0]
  b64_data = base64.b64encode(data).decode('utf-8')

  print('b64_data', b64_data)
  return {
    'image': b64_data,
  }

if __name__ == '__main__':
  runpod.serverless.start({'handler': handler })