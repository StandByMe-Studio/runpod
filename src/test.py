import requests
import base64
import sys
import json
import imageio
from moviepy import ImageSequenceClip
import time
from datetime import datetime


headers = {
  "accept": "application/json",
  "authorization": "RTJJVUQCVWVAFMWE3IT8USFJ23M3XPJOVUH5US23",  # 你的 API Key
  "content-type": "application/json"
}

# endpoint_id = 'zniyke51ptmvr1'
endpoint_id = 'g894rwjtg8i29l'


def webp_to_mp4(webp_file, mp4_file):
  # 读取动态 webp 的每一帧
  frames = []
  reader = imageio.get_reader(webp_file)
  for frame in reader:
      frames.append(frame)

  # 使用 moviepy 把帧序列写成 mp4
  clip = ImageSequenceClip(frames, fps=reader.get_meta_data().get("fps", 16))
  clip.write_videofile(mp4_file, codec='libx264')


def run_sample():
  return {
    "input": {
      "mode": "sample",
      "prompt": 'beautiful girl,'
    }
  }

def run_mp4():
  with open('input.jpg', 'rb') as f:
    data = f.read()
  image_b64 = base64.b64encode(data).decode('utf-8')
  return {
    'input': {
      'mode': 'mp4',
      # 'prompt': 'Skirt lifts, legs spread, breasts jiggle, expression changes from stern to playful.',
      'prompt': 'Head tilts, lips moisten, dress shimmers, cocktail glass moves slightly',
      'image': image_b64,
    }
  }


def run(mode):
  start_at = int(time.time())
  if mode == 'sample':
    payload = run_sample()
  elif mode == 'mp4':
    payload = run_mp4()
  else:
    return

  url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
  print('url', url, 'payload', payload)
  response = requests.post(url, headers=headers, json=payload)
  print(response.json())
  request_id = response.json()['id']
  while True:
    if query(request_id): break
    time.sleep(10)

  end_at = int(time.time())
  print('start_at', datetime.fromtimestamp(start_at).strftime('%Y-%m-%d %H:%M:%S'))
  print('end_at', datetime.fromtimestamp(end_at).strftime('%Y-%m-%d %H:%M:%S'))
  print('cost', end_at - start_at)

  # data = response.json()
  # print(data)
  # image_data = base64.b64decode(data['output']['image'])
  # with open('output.png', 'wb') as f:
  #   f.write(image_data)
  # print('done...')


def query(request_id):
  print('query', request_id)
  url = f'https://api.runpod.ai/v2/{endpoint_id}/status/{request_id}'
  response = requests.get(url, headers=headers)
  jd = response.json()
  print(jd['status'])
  if jd['status'] == 'FAILED':
    print(jd['error'])
    return True
  if jd['status'] != 'COMPLETED': return False
  
  success = jd['output']['success']
  if not success:
    print(jd['output']['error'])
    return True

  mode = jd['output']['mode']
  image_b64 = jd['output']['image']
  if mode == 'sample':
    with open('output.png', 'wb') as f:
      f.write(base64.b64decode(image_b64))
  elif mode == 'mp4':
    with open('output.webp', 'wb') as f:
      f.write(base64.b64decode(image_b64))
    webp_to_mp4('output.webp', 'output.mp4')
  print('done...')
  return True


if __name__ == '__main__':
  if sys.argv[1] == 'query':
    query(sys.argv[2])
  elif sys.argv[1] == 'run':
    run(sys.argv[2])
