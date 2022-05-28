from flask import Flask
from flask_restful import Api, Resource, reqparse
import docx2txt
from pathlib import Path
import mysql.connector
import PySimpleGUI as sg
from tkinter import * 
import os
import re

mydb = mysql.connector.connect(
    host="eyvqcfxf5reja3nv.cbetxkdyhwsb.us-east-1.rds.amazonaws.com",
    user="gjnk9aymcgsx16c8",
    password="wctb0rl370s5b602",
    database="e7aariv527gxjb0w"
)


app = Flask(__name__)
api = Api(app)

last_files = []
rules = ['срок сдачи до', 'выполнить до', 'подготовить ответ к', 'выполнить до', 'сообщить до', 'согласовать до']# Правила для определения дат
email = ''
telegram_id = []

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
    local_files = []

    for document in files: # Перебор файлов
        date = read_docs(str(folder) + '/' + document)
        obj = {
            'name': document,
            'date': date,
        }
        local_files.append(obj)

    mycursor = mydb.cursor()
    mycursor.execute(f"""select name, date from documents""")
    db_files = mycursor.fetchall()
    db_files_list = []
    for file in db_files:
        db_files_list.append({'name':file[0], 'date':file[1]})
    copy_db_list = db_files_list
    print('email = ', email)
    print('telegram_id = ', telegram_id)

    for file in local_files:
        if file in db_files_list:
             copy_db_list.remove(file)
        else:
            mycursor.execute(f"""
                INSERT INTO documents (name, date, visible, email, userID, chatID)
                VALUES ('{file['name']}', '{file['date']}', '{True}', '{email}', '{telegram_id[0]}', '{telegram_id[1]}');
            """)
            mydb.commit()

    for file in copy_db_list:
        mycursor.execute(f"""
            delete from documents
            where name='{file['name']}';
        """)
        mydb.commit()

def get_database_data():
    mycursor = mydb.cursor()
    mycursor.execute(f"""select * from documents""")
    db_files = mycursor.fetchall()
    files_list = []

    for file in db_files:
        files_list.append({'id': file[0], 'name':file[1], 'date':file[2], 'visible': file[3], 'email': file[4], 'telegramId': [file[5], file[6]]})
    return files_list

class Documents(Resource):
    def get(self, id=0):
        files_enum(Path(__file__).parent/'university-documents')
        files_list = get_database_data()
        if id == 0:
            return files_list, 200
        for file in files_list:
            if file['id'] == id:
                return file, 200
        return 'File not found', 400

    def post(self, id):
      files_enum(Path(__file__).parent/'university-documents')
      current_files = get_database_data()
      parser = reqparse.RequestParser()
      parser.add_argument("name")
      parser.add_argument("date")
      parser.add_argument("visible")
      params = parser.parse_args()
      for file in current_files:
          if(id == file["id"]):
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
      files_enum(Path(__file__).parent/'university-documents')
      current_files = get_database_data()
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
        files_enum(Path(__file__).parent/'university-documents')
        current_files = get_database_data()
        current_files = [file for file in current_files if file["id"] != id]
        return f"File with id {id} is deleted.", 200


api.add_resource(Documents, "/document-service", "/document-service/", "/document-service/<int:id>")



layout = [
    [sg.Text('Введите электронную почту SFEDU'), sg.InputText()],
    [sg.Text('Введите user ID от телеграма'), sg.InputText()],
    [sg.Text('Введите chat ID от телеграма'), sg.InputText()],
    [sg.Text('(чтобы узнать свой id необходимо зайти в приложение телеграм и вызвать бота "Get my ID")')],
    [sg.Submit(), sg.Cancel()]
]
window = sg.Window('Document Service', layout)


if __name__ == '__main__':
    event, values = window.read()
    if event in (None, 'Submit', 'Exit', 'Cancel'):
        window.close()
    email = values[0]
    telegram_id = [values[1], values[2]]
    files_enum(Path(__file__).parent/'university-documents')
    app.run(debug=True, use_reloader=False)
