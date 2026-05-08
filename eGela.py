# -*- coding: UTF-8 -*-
from tkinter import messagebox
import requests
import urllib
from urllib.parse import unquote
import bs4
import time
import helper

class eGela:
    _login = 0
    _cookie = ""
    _curso = ""
    _refs = []
    _root = None

    def __init__(self, root):
        self._root = root

    def check_credentials(self, username, password, event=None):
        popup, progress_var, progress_bar = helper.progress("check_credentials", "Logging into eGela...")
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
            'username': username.get(),
            'password': password.get(),
            'logintoken': logintoken
        }
        respuesta2 = requests.request(metodo, uri, headers=cabeceras, data=cuerpo, allow_redirects=False)

        print('------------------------')
        print(f'Solicitud2:\n\t{metodo} {uri}')
        print(f"\tEnviando credenciales del usuario: {cuerpo['username']}")
        print(f'Respuesta2:\n\t{respuesta2.status_code} {respuesta2.reason}')
        
        
        #print(f'\t{respuesta2.headers["Location"]}\n\t{respuesta2.headers["Set-Cookie"]}')

        if respuesta2.status_code == 303:
            # Obtenemos la cabecera Location
            location = respuesta2.headers['Location']
            if "Set-Cookie" in respuesta2.headers:
                MoodleSessionegela = respuesta2.headers['Set-Cookie'].split('MoodleSessionegela=')[1].split(';')[0]
        else:
            print("Error al autenticarse. Revisa tus credenciales.")
            popup.destroy()
            messagebox.showinfo("Alert Message", "Login incorrect!")
            return

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
        #print(f'\t{respuesta3.headers["Location"]}')

        if respuesta3.status_code != 303:
            print("Error al autenticarse.")
            popup.destroy() 
            messagebox.showinfo("Alert Message", "Login incorrect!") 
            return
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
        popup, progress_var, progress_bar = helper.progress("get_pdf_refs", "Downloading PDF list...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("\n##### 4. PETICION (Página principal de la asignatura en eGela) #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        metodo = "GET"
        uri = self._curso
        cabeceras = {
            "Cookie": f"MoodleSessionegela={self._cookie}"
        }

        respuesta = requests.request(metodo, uri, headers=cabeceras, allow_redirects=False)

        print("------------------------")
        print(f"Solicitud:\n\t{metodo} {uri}")
        print(f"Respuesta:\n\t{respuesta.status_code} {respuesta.reason}")

        if respuesta.status_code != 200:
            print("Error al acceder a la página principal de la asignatura.")
            print(respuesta.status_code)
            popup.destroy()
            return self._refs

        print("\n##### Analisis del HTML... #####")
        #############################################
        # ANALISIS DE LA PAGINA DEL AULA EN EGELA
        # PARA BUSCAR PDFs
        #############################################

        soup_principal = bs4.BeautifulSoup(respuesta.text, "html.parser")

        self._refs = []

        urls_secciones = [self._curso]

        for enlace in soup_principal.find_all("a"):
            href = enlace.get("href")
            # Identificamos los enlaces que llevan a las otras pestañas
            if href is not None and "course/view.php?id=" in href and "&section=" in href:
                if href not in urls_secciones:
                    urls_secciones.append(href)

        # CALCULAR EL AVANCE DE LA BARRA DE PROGRESO
        if len(urls_secciones) > 0:
            progress_step = float(100.0 / len(urls_secciones))
        else:
            progress_step = 100.0

        recursos_procesados = []

        # BUCLE PRINCIPAL: ENTRAR EN CADA PESTAÑA
        for url_seccion in urls_secciones:
            
            # Descargamos el HTML de esta pestaña en concreto
            resp_sec = requests.request("GET", url_seccion, headers=cabeceras, allow_redirects=False)
            soup_sec = bs4.BeautifulSoup(resp_sec.text, "html.parser")

            # Buscamos los PDFs dentro de esta pestaña
            for enlace in soup_sec.find_all("a"):
                href = enlace.get("href")

                if href is not None and "mod/resource/view.php" in href:
                    
                    # Evitamos descargar el mismo PDF dos veces si eGela lo repite
                    if href not in recursos_procesados:
                        recursos_procesados.append(href)

                        respuesta_pdf = requests.request(
                            "GET",
                            href,
                            headers=cabeceras,
                            allow_redirects=False
                        )

                        if respuesta_pdf.status_code == 303:
                            pdf_link = respuesta_pdf.headers["Location"]
                            pdf_name = pdf_link.split("/")[-1]
                            pdf_name = unquote(pdf_name)

                            if pdf_name.lower().endswith(".pdf"):
                                self._refs.append({
                                    "pdf_name": pdf_name,
                                    "pdf_link": pdf_link
                                })
                                print(f"{pdf_name} -> {pdf_link}")
            progress += progress_step
            progress_var.set(progress)
            progress_bar.update()

        popup.destroy()
        return self._refs

    def get_pdf(self, selection):

        print("\t##### descargando  PDF... #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################
        cabeceras = {
            'Cookie': f'MoodleSessionegela={self._cookie}'
        }
        pdf_object = self._refs[selection]
        pdf_name = pdf_object['pdf_name']
        pdf_link = pdf_object['pdf_link']
        pdf_response = requests.request('GET', pdf_link, headers=cabeceras)
        pdf_content = pdf_response.content

        return pdf_name, pdf_content