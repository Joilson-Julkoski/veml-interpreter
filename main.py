import requests
from dotenv import dotenv_values

config = dotenv_values(".env")

url = "https://api.lemonfox.ai/v1/audio/transcriptions"
headers = {
  "Authorization": f"Bearer {config['LEAMON_FOX_API_KEY']}"
}

data = {
  "language": "portuguese",
  "response_format": "verbose_json",
  "timestamp_granularities[]": "word"
}


files = {"file": open("teste.mp3", "rb")}
response = requests.post(url, headers=headers, files=files, data=data)

print(response.json())

# To upload a local file add the files parameter:
