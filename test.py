import json

with open('result.json' , 'r') as fp:
    data = json.load(fp)

faceId = data[0]['faceId']

print(faceId)