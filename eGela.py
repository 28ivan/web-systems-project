# -*- coding: UTF-8 -*-
from tkinter import messagebox
import requests
import urllib
from urllib.parse import unquote
import  bs4
import time
import helpers

class eGela:
    _login = 0
    _cookie = ""
    _curso = ""
    _refs = []
    _root = None

    def __init__(self, root):
        self._root = root

    def check_credentials(self, username, password, event=None):
        popup, progress_var, progress_bar = helpers.progress("check_credentials", "Logging into eGela...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("##### 1. PETICION #####")
        metodo = 'GET'
        uri = "https://egela.ehu.eus/login/index.php"
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        respuesta1 = requests.request(metodo, uri, allow_redirects=False)
        print('------------------------')
        print(f'Solicitud1:\n\t{metodo} {uri}')
        print(f'Respuesta1:\n\t{respuesta1.status_code} {respuesta1.reason}')

        if respuesta1.status_code == 200:
            # Obtenemos la MoodleSessionegela y el logintoken
            # Cabecera SetCookie: MoodleSessionegela
            cookie = respuesta1.headers['Set-Cookie']
            MoodleSessionegela = cookie.split("MoodleSessionegela=")[1].split(";")[0]
            # logintoken campo input del fomulario
            token = bs4.BeautifulSoup(respuesta1.text, "html.parser")
            logintoken = token.find("input", {"name": "logintoken"})["value"]
        else:
            print("Error al obtener MoodleSessionegela y logintoken.")
            print(respuesta1.status_code)
            exit(1)

        progress = 25
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)


        print("\n##### 2. PETICION #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        metodo = 'POST'
        uri = "https://egela.ehu.eus/login/index.php"
        cabeceras = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': f'MoodleSessionegela={MoodleSessionegela}'
        }
        cuerpo = {
            'username': username,
            'password': password,
            'logintoken': logintoken
        }
        respuesta2 = requests.request(metodo, uri, headers=cabeceras, data=cuerpo, allow_redirects=False)

        print('------------------------')
        print(f'Solicitud2:\n\t{metodo} {uri}')
        print(f'\t{cuerpo}')
        print(f'Respuesta2:\n\t{respuesta2.status_code} {respuesta2.reason}')
        print(f'\t{respuesta2.headers["Location"]}\n\t{respuesta2.headers["Set-Cookie"]}')

        if respuesta2.status_code == 303:
            # Obtenemos la cabecera Location
            location = respuesta2.headers['Location']
            MoodleSessionegela = respuesta2.headers['Set-Cookie'].split('MoodleSessionegela=')[1].split(';')[0]
        else:
            print("Error al autenticarse.")
            print(respuesta2.status_code)
            exit(1)

        progress = 50
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)

        print("\n##### 3. PETICION #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        metodo = 'GET'
        uri = location
        cabeceras = {
            'Cookie': f'MoodleSessionegela={MoodleSessionegela}'
        }
        respuesta3 = requests.request(metodo, uri, headers=cabeceras, allow_redirects=False)

        print('------------------------')
        print(f'Solicitud3:\n\t{metodo} {uri}')
        print(f'Respuesta3:\n\t{respuesta3.status_code} {respuesta3.reason}')
        print(f'\t{respuesta3.headers["Location"]}')

        if respuesta3.status_code != 303:
            print("Error al autenticarse.")
            print(respuesta3.status_code)
            # print(respuesta3.text)
            exit(1)
        else:
            # Obtenemos la cabecera Location
            location = respuesta3.headers['Location']

        progress = 75
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)
        popup.destroy()

        print("\n##### 4. PETICION #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        metodo = 'GET'
        uri = location
        cabeceras = {
            'Cookie': f'MoodleSessionegela={MoodleSessionegela}'
        }
        respuesta4 = requests.request(metodo, uri, headers=cabeceras, allow_redirects=False)

        print('------------------------')
        print(f'Solicitud4:\n\t{metodo} {uri}')
        print(f'Respuesta4:\n\t{respuesta4.status_code} {respuesta4.reason}')

        if respuesta4.status_code != 200:
            print("Error al buscar el nombre.")
            exit(1)
        else:
            COMPROBACION_DE_LOG_IN = True
            soup = bs4.BeautifulSoup(respuesta4.text, 'html.parser')
            enlaces = soup.find_all('a')
            for enlace in enlaces:
                if "Sistemas Web" in enlace.text:
                    uri_curso = enlace.get('href')



        progress = 100
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)
        popup.destroy()


        if COMPROBACION_DE_LOG_IN:
            #############################################
            # ACTUALIZAR VARIABLES
            #############################################
            self._root.destroy()
            self._login = 1
            self._cookie = MoodleSessionegela
            self._curso = uri_curso
        else:
            messagebox.showinfo("Alert Message", "Login incorrect!")

    def get_pdf_refs(self):
        popup, progress_var, progress_bar = helpers.progress("get_pdf_refs", "Downloading PDF list...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("\n##### 4. PETICION (Página principal de la asignatura en eGela) #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################


        progress_step = float(100.0 / len(NUMERO_DE_PDF_EN_EGELA))


        print("\n##### Analisis del HTML... #####")
        #############################################
        # ANALISIS DE LA PAGINA DEL AULA EN EGELA
        # PARA BUSCAR PDFs
        #############################################

        # INICIALIZA Y ACTUALIZAR BARRA DE PROGRESO
        # POR CADA PDF ANIADIDO EN self._refs

        progress_step = float(100.0 / len(NUMERO_DE_PDF_EN_EGELA))


                progress += progress_step
                progress_var.set(progress)
                progress_bar.update()
                time.sleep(0.1)

        popup.destroy()
        return self._refs

    def get_pdf(self, selection):

        print("\t##### descargando  PDF... #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        return pdf_name, pdf_content