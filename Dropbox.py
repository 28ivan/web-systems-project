import requests
import urllib
import webbrowser
from socket import AF_INET, socket, SOCK_STREAM
import json
import helper

app_key = ''
app_secret = ''
server_addr = "localhost"
server_port = 8070
redirect_uri = "http://" + server_addr + ":" + str(server_port)

class Dropbox:
    _access_token = ""
    _path = "/"
    _files = []
    _root = None
    _msg_listbox = None

    def __init__(self, root):
        self._root = root

    def local_server(self):
        # por el puerto 8090 esta escuchando el servidor que generamos
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((server_addr, server_port))
        server_socket.listen(1)
        print("\tLocal server listening on port " + str(server_port))

        # recibe la redireccio 302 del navegador
        client_connection, client_address = server_socket.accept()
        peticion = client_connection.recv(1024)
        print("\tRequest from the browser received at local server:")
        print (peticion)

        # buscar en solicitud el "auth_code"
        primera_linea =peticion.decode('UTF8').split('\n')[0]
        aux_auth_code = primera_linea.split(' ')[1]
        auth_code = aux_auth_code[7:].split('&')[0]
        print ("\tauth_code: " + auth_code)

        # devolver una respuesta al usuario
        http_response = "HTTP/1.1 200 OK\r\n\r\n" \
                        "<html>" \
                        "<head><title>Proba</title></head>" \
                        "<body>The authentication flow has completed. Close this window.</body>" \
                        "</html>"
        client_connection.sendall(http_response.encode('utf-8'))
        client_connection.close()
        server_socket.close()

        return auth_code

    def do_oauth(self):
        #############################################
        # RELLENAR CON CODIGO DE LAS PETICIONES HTTP
        # Y PROCESAMIENTO DE LAS RESPUESTAS HTTP
        # PARA LA OBTENCION DEL ACCESS TOKEN
        #############################################

        url = f"https://www.dropbox.com/oauth2/authorize?response_type=code&client_id={app_key}&redirect_uri={urllib.parse.quote(redirect_uri)}"
        webbrowser.open(url)
        auth_code = self.local_server()
        params = {
            'code': auth_code,
            'grant_type': 'authorization_code',
            'client_id': app_key,
            'client_secret': app_secret,
            'redirect_uri': redirect_uri
        }
        cabeceras = {
            'User-Agent': 'Python Client',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        uri = 'https://api.dropboxapi.com/oauth2/token'
        response = requests.post(uri, data=params, headers=cabeceras)
        json_response = json.loads(response.content)
        self._access_token = json_response['access_token']

        self._root.destroy()

    def list_folder(self, msg_listbox):
        print("/list_folder")
        uri = 'https://api.dropboxapi.com/2/files/list_folder'
        # https://www.dropbox.com/developers/documentation/http/documentation#files-list_folder
        
        # LIMPIEZA DE LA RUTA 
        self._path = self._path.replace("\\", "/").replace("//", "/").strip()
        if self._path.endswith("/") and len(self._path) > 1:
            self._path = self._path.rstrip("/")
        #
        cabeceras = {
            'Authorization': f'Bearer {self._access_token}',
            'Content-Type': 'application/json'
        }

        ruta_dropbox = "" if self._path == "/" else self._path
        
        cuerpo = {
            "path": ruta_dropbox,
            "recursive": False,
            "include_media_info": False,
            "include_deleted": False,
            "include_has_explicit_shared_members": False
        }
        respuesta = requests.post(uri, headers=cabeceras, json=cuerpo)
        print(f"Respuesta list_folder: {respuesta.status_code}")
        if respuesta.status_code == 200:
            contenido_json = respuesta.json()
            self._files = helper.update_listbox2(msg_listbox, self._path, contenido_json)
        else:
            print("Error al listar archivos de Dropbox:")
            print(respuesta.text)

    def transfer_file(self, file_path, file_data):
        print("/upload")
        uri = 'https://content.dropboxapi.com/2/files/upload'
        # https://www.dropbox.com/developers/documentation/http/documentation#files-upload
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################
        # Configuramos las cabeceras. La subida de archivos en Dropbox es especial:
        # Pide que los datos de la ruta vayan en una cabecera llamada 'Dropbox-API-Arg'
        # y que el tipo de contenido sea 'application/octet-stream' (datos binarios)
        cabeceras = {
            'Authorization': f'Bearer {self._access_token}',
            'Content-Type': 'application/octet-stream',
            'Dropbox-API-Arg': json.dumps({
                "path": file_path,
                "mode": "add",
                "autorename": True,
                "mute": False
            })
        }

        # POST con data=file_data porque se manda un PDF no un JSON
        respuesta = requests.post(uri, headers=cabeceras, data=file_data)

        print(f"Respuesta transfer_file: {respuesta.status_code}")
        if respuesta.status_code != 200:
            print("Error al subir el archivo:")
            print(respuesta.text)

    def delete_file(self, file_path):
        print("/delete_file")
        uri = 'https://api.dropboxapi.com/2/files/delete_v2'
        # https://www.dropbox.com/developers/documentation/http/documentation#files-delete
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        cabeceras = {
            'Authorization': f'Bearer {self._access_token}',
            'Content-Type': 'application/json'
        }

        cuerpo = {
            "path": file_path
        }

        respuesta = requests.post(uri, headers=cabeceras, json=cuerpo)
        
        print(f"Respuesta delete_file: {respuesta.status_code}")
        
        if respuesta.status_code != 200:
            print("Error al borrar el archivo en Dropbox:")
            print(respuesta.text)

    def create_folder(self, path):
        print("/create_folder")
        uri = 'https://api.dropboxapi.com/2/files/create_folder_v2'
       # https://www.dropbox.com/developers/documentation/http/documentation#files-create_folder
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################
        # Limpiar el path, se quitan dobles barras, barras invertidas y espacios al principio/final
        path = path.replace("\\", "/").replace("//", "/").strip()
        if path.endswith("/") and len(path) > 1:
            path = path.rstrip("/")
        self._path = path
        
        cabeceras = {
            'Authorization': f'Bearer {self._access_token}',
            'Content-Type': 'application/json'
        }

        cuerpo = {
            "path": path,
            "autorename": False
        }

        respuesta = requests.post(uri, headers=cabeceras, json=cuerpo)

        print(f"Respuesta create_folder: {respuesta.status_code}")
        
        if respuesta.status_code != 200:
            print("Error al crear la carpeta en Dropbox:")
            print(respuesta.text)