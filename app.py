from flask import Flask
from flask_restful import Api, Resource, reqparse
import docx2txt
import os
import re

app = Flask(__name__)
api = Api(app)

last_files = []
rules = ['срок сдачи до', 'выполнить до', 'подготовить ответ к', 'выполнить до', 'сообщить до', 'согласовать до']# Правила для определения дат

def parse_txt(path):
    text = open(path).read()
    date = ''
    for rule in rules: # Перебор правил
        if rule in text:
            date = text[text.index(rule):]
            date = str(re.search(r'\d\d.\d\d.\d\d\d\d', date).group())
    return date

def parse_docx(path):
    text = docx2txt.process(path)
    date = ''
    for rule in rules: # Перебор правил
        if re.search(rule, text):
            date = text[text.index(rule):]
            date = str(re.search(r'\d\d.\d\d.\d\d\d\d', date).group())
    return date

def read_docs(path):
    filename, file_extension = os.path.splitext(path)
    date = '';
    if file_extension == '.docx':
        date = parse_docx(path)
    if file_extension == '.txt':
        date = parse_txt(path)
    return date

def files_enum(folder):
    files = os.listdir(folder)
    output = {'files': []}
    id = 1
    for document in files: # Перебор файлов
        date = read_docs(folder + '\\' + document)
        obj = {
            'name': document,
            'date': date,
            'visible': True,
            'id': id
        }
        output['files'].append(obj)
        id = id + 1
    return output

class Documents(Resource):
    def get(self, id=0):
        current_files = files_enum(r'C:\Users\Ekaterina\Desktop\sfedu-documents')

        if id == 0:
            return current_files, 200
        for file in current_files:
            return file, 200
        return "File not found", 404

    def post(self, id):
      current_files = files_enum(r'C:\Users\Ekaterina\Desktop\sfedu-documents')
      parser = reqparse.RequestParser()
      parser.add_argument("name")
      parser.add_argument("date")
      parser.add_argument("visible")
      params = parser.parse_args()
      for file in current_files:
          if id == file["id"]:
              return f"File with id {id} already exists", 400

          file = {
              "id": int(id),
              "name": params["name"],
              "date": params["date"],
              "visible": params["visible"]
          }

          current_files.append(file)
      return file, 201

    def put(self, id):
      current_files = files_enum(r'C:\Users\Ekaterina\Desktop\sfedu-documents')
      parser = reqparse.RequestParser()
      parser.add_argument("name")
      parser.add_argument("date")
      parser.add_argument("visible")
      params = parser.parse_args()
      for file in current_files:
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
        current_files = files_enum(r'C:\Users\Ekaterina\Desktop\sfedu-documents')
        current_files = [file for file in current_files if file["id"] != id]
        return f"File with id {id} is deleted.", 200


api.add_resource(Documents, "/document-service", "/document-service/", "/document-service/<int:id>")

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
    # current_files = files_enum(r'C:\Users\Ekaterina\Desktop\sfedu-documents')
