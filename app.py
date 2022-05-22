from flask import Flask
from flask_restful import Api, Resource, reqparse
import random
import os
import re

app = Flask(__name__)
api = Api(app)

last_files = []


def files_enum(folder):
    files = os.listdir(folder)
    output = {'files': []}
    rules = ['[0-9][0-9]_[0-9][0-9]_[0-9][0-9][0-9][0-9]'] # Правила для определения дат в названии
    id = 1
    for file in files: # Перебор файлов
        for rule in rules: # Перебор правил
            date = '';

            if re.search(rule, file):
                date = str(re.search(rule, file).group(0))
                date = date[6:] + '-' + date[3:5] + '-' + date[:2] # Форматирование даты из дд_мм_гггг в гггг-мм-дд

            obj = {
                'name': file,
                'date': date,
                'visible': True,
                'id': id
            }
            output['files'].append(obj)
            id = id + 1

    return output['files']

# def send(files):
#     print(files)

class Documents(Resource):
    def get(self, id=0):
        if id == 0:
            return current_files, 200
        for file in current_files:
            return file, 200
        return "File not found", 404

    def post(self, id):
      parser = reqparse.RequestParser()
      parser.add_argument("name")
      parser.add_argument("date")
      parser.add_argument("visible")
      params = parser.parse_args()
      for file in last_files:
          if(id == file["id"]):
              return f"File with id {id} already exists", 400
      file = {
          "id": int(id),
          "name": params["name"],
          "date": params["date"],
          "visible": params["visible"]
      }
      last_files.append(file)
      return file, 201

    def put(self, id):
      parser = reqparse.RequestParser()
      parser.add_argument("name")
      parser.add_argument("date")
      parser.add_argument("visible")
      params = parser.parse_args()
      for file in last_files:
          if(id == file["id"]):
              file["name"] = params["name"]
              file["date"] = params["date"]
              file["visible"] = params["visible"]
              return file, 200

      file = {
          "id": id,
          "name": params["name"],
          "date": params["date"],
          "visible": params["visible"]
      }

    def delete(self, id):
        global last_files
        last_files = [file for file in last_files if file["id"] != id]
        return f"File with id {id} is deleted.", 200


api.add_resource(Documents, "/document-service", "/document-service/", "/document-service/<int:id>")

while True:
    current_files = files_enum(r'C:\Users\Ekaterina\Desktop\sfedu-documents')
    # if last_files != current_files:
    #     send(current_files)
    last_files = current_files
    app.run(debug=True)
