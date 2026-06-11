import curses
import subprocess
import os

# ==========================================
# 1. FUNCIONES LÓGICAS (CALLBACKS DE PYTHON)
# ==========================================
def agregar_usuario_samba():
    usuario = input("\n[+] Ingrese el nombre de usuario (debe existir en el sistema Linux): ")
    if usuario.strip():
        os.system(f"sudo smbpasswd -a {usuario}")
    else:
        print("\n[-] Operación cancelada. Nombre vacío.")

def eliminar_usuario_samba():
    usuario = input("\n[+] Ingrese el nombre del usuario a eliminar de Samba: ")
    if usuario.strip():
        os.system(f"sudo smbpasswd -x {usuario}")
    else:
        print("\n[-] Operación cancelada. Nombre vacío.")

def cambiar_propietario_carpeta():
    ruta = input("\n[+] Ingrese la ruta absoluta de la carpeta compartida (ej. /srv/samba/shared): ")
    if os.path.isdir(ruta):
        propietario = input("[+] Ingrese el nuevo Propietario:Grupo (ej. root:smbgroup): ")
        if propietario.strip():
            os.system(f"sudo chown -R {propietario} '{ruta}'")
            print(f"\n[*] Propietario actualizado para {ruta}.")
        else:
            print("\n[-] Operación cancelada.")
    else:
        print(f"\n[!] Error: El directorio {ruta} no existe.")

def cambiar_permisos_carpeta():
    ruta = input("\n[+] Ingrese la ruta absoluta de la carpeta compartida: ")
    if os.path.isdir(ruta):
        permisos = input("[+] Ingrese los permisos en formato octal (ej. 775 o 777): ")
        if permisos.strip():
            os.system(f"sudo chmod -R {permisos} '{ruta}'")
            print(f"\n[*] Permisos actualizados para {ruta}.")
        else:
            print("\n[-] Operación cancelada.")
    else:
        print(f"\n[!] Error: El directorio {ruta} no existe.")

def reiniciar_servicio_samba():
    print("[*] Verificando sintaxis de smb.conf antes de reiniciar...\n")
    resultado = os.system("testparm -s > /dev/null 2>&1")
    
    if resultado == 0:
        print("[*] Sintaxis correcta. Reiniciando servicios...")
        os.system("sudo systemctl restart smbd nmbd")
        print("\n[+] Samba se ha reiniciado correctamente.")
    else:
        print("\n[!] Error en smb.conf. El servicio NO se reiniciará para evitar caídas.")

# ==========================================
# 2. CLASES DE ACCIÓN (COMMAND PATTERN)
# ==========================================
class AccionBash:
    def __init__(self, nombre, comando):
        self.nombre = nombre
        self.comando = comando

    def ejecutar(self):
        curses.endwin()
        os.system('clear')
        
        print(f"[*] Ejecutando: {self.nombre}")
        print("=" * 60 + "\n")
        
        try:
            subprocess.run(self.comando, shell=True)
        except Exception as e:
            print(f"[!] Error crítico al ejecutar: {e}")
            
        print("\n" + "=" * 60)
        print("\n[[-] Presiona ENTER para regresar al menú...]")
        input()

class AccionPython:
    def __init__(self, nombre, funcion, *args, **kwargs):
        self.nombre = nombre
        self.funcion = funcion
        self.args = args
        self.kwargs = kwargs

    def ejecutar(self):
        curses.endwin()
        os.system('clear')
        
        print(f"[*] Modo Interactivo: {self.nombre}")
        print("=" * 60)
        
        try:
            self.funcion(*self.args, **self.kwargs)
        except Exception as e:
            print(f"\n[!] Error crítico en la función: {e}")
            
        print("\n" + "=" * 60)
        print("\n[[-] Presiona ENTER para regresar al menú...]")
        input()

# ==========================================
# 3. SISTEMA DE MENÚS (TUI Engine)
# ==========================================
class Menu:
    def __init__(self, titulo):
        self.titulo = titulo
        self.opciones = [] 
        self.indice_actual = 0

    def agregar_opcion(self, nombre, destino):
        self.opciones.append((nombre, destino))

class AplicacionTUI:
    def __init__(self, stdscr, menu_raiz):
        self.stdscr = stdscr
        self.pila_menus = [menu_raiz] 
        curses.curs_set(0)
        self.stdscr.keypad(True)
        
        # Inicialización de colores (Fondo negro, letras verdes)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)

    def dibujar_interfaz(self):
        self.stdscr.clear()
        alto, ancho = self.stdscr.getmaxyx()
        
        color_verde = curses.color_pair(1)

        # Validación de tamaño de terminal
        if alto < 25 or ancho < 75:
            mensaje = "Terminal muy pequeña. Agrándala para usar el sysadmin."
            try:
                self.stdscr.addstr(alto//2, max(0, (ancho//2) - (len(mensaje)//2)), mensaje, color_verde)
            except curses.error: pass
            self.stdscr.refresh()
            return False

        # --- 1. DIBUJAR MARGEN VERDE (Box) ---
        self.stdscr.attron(color_verde)
        self.stdscr.border(0, 0, 0, 0, 0, 0, 0, 0)
        self.stdscr.attroff(color_verde)

        menu_actual = self.pila_menus[-1]
        
        # --- 2. ARTE ASCII ---
        arte_ascii = [
r"███████╗ █████╗ ███╗   ███╗██████╗  █████╗ ",
r"██╔════╝██╔══██╗████╗ ████║██╔══██╗██╔══██╗",
r"███████╗███████║██╔████╔██║██████╔╝███████║",
r"╚════██║██╔══██║██║╚██╔╝██║██╔══██╗██╔══██║",
r"███████║██║  ██║██║ ╚═╝ ██║██████╔╝██║  ██║",
r"╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═════╝ ╚═╝  ╚═╝"

        ]

        titulo = f"=== {menu_actual.titulo} ==="
        if len(self.pila_menus) > 1:
            subtitulo = "[ ↑/↓: Navegar | ESPACIO: Seleccionar | ←: Volver | Q: Salir ]"
        else:
            subtitulo = "[ ↑/↓: Navegar | ESPACIO: Seleccionar | Q: Salir ]"

        # --- 3. CÁLCULO PARA CENTRAR VERTICALMENTE ---
        elementos_totales = len(arte_ascii) + 5 + len(menu_actual.opciones)
        y_inicial = (alto // 2) - (elementos_totales // 2)

        # Dibujar Arte ASCII en verde
        self.stdscr.attron(color_verde)
        for i, linea in enumerate(arte_ascii):
            x = (ancho // 2) - (len(linea) // 2)
            self.stdscr.addstr(y_inicial + i, x, linea)
        self.stdscr.attroff(color_verde)

        # Dibujar Títulos
        y_titulo = y_inicial + len(arte_ascii) + 2
        self.stdscr.addstr(y_titulo, (ancho // 2) - (len(titulo) // 2), titulo, curses.A_BOLD | curses.A_UNDERLINE)
        self.stdscr.addstr(y_titulo + 1, (ancho // 2) - (len(subtitulo) // 2), subtitulo)

        # --- 4. DIBUJAR OPCIONES DE MENÚ ---
        y_opciones = y_titulo + 3
        for i, (nombre, _) in enumerate(menu_actual.opciones):
            texto = f" {i+1}. {nombre} "
            x = (ancho // 2) - (len(texto) // 2)
            
            if i == menu_actual.indice_actual:
                self.stdscr.addstr(y_opciones + i, x, f">>{texto}<<", curses.A_REVERSE | curses.A_BOLD)
            else:
                self.stdscr.addstr(y_opciones + i, x, f"  {texto}  ")

        self.stdscr.refresh()
        return True

    def ejecutar(self):
        while True:
            espacio_suficiente = self.dibujar_interfaz()
            tecla = self.stdscr.getch()
            
            if not espacio_suficiente:
                if tecla in [ord('q'), ord('Q')]: break
                continue

            menu_actual = self.pila_menus[-1]

            if tecla == curses.KEY_UP and menu_actual.indice_actual > 0:
                menu_actual.indice_actual -= 1
            elif tecla == curses.KEY_DOWN and menu_actual.indice_actual < len(menu_actual.opciones) - 1:
                menu_actual.indice_actual += 1
            elif tecla == ord(' '):
                destino_seleccionado = menu_actual.opciones[menu_actual.indice_actual][1]
                
                if isinstance(destino_seleccionado, Menu):
                    self.pila_menus.append(destino_seleccionado)
                elif isinstance(destino_seleccionado, (AccionBash, AccionPython)):
                    destino_seleccionado.ejecutar()
                    
            elif tecla == curses.KEY_LEFT or tecla == ord('b') or tecla == curses.KEY_BACKSPACE:
                if len(self.pila_menus) > 1:
                    self.pila_menus.pop()
            elif tecla in [ord('q'), ord('Q')]:
                break 

# ==========================================
# 4. ÁRBOL DE MENÚS Y COMPILACIÓN
# ==========================================
def main(stdscr):

    # Comandos compuestos en Bash para replicar la funcionalidad del script original
    cmd_recursos = (
        "echo '[-] RAM Memory Usage:' && free -h && "
        "echo '\n[-] Disk Space (Main folders):' && df -h | grep -E '^/dev|Filesystem' && "
        "echo '\n[-] Top 5 CPU Consuming Processes:' && ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%cpu | head -n 6"
    )

    cmd_listar_samba = "sudo pdbedit -L -v | grep -E 'Unix username|Account desc'"
    cmd_estado_samba = "sudo systemctl status smbd --no-pager | head -n 15"

    # --- Submenú: Administración de Accesos ---
    menu_usuarios = Menu("ADMINISTRACIÓN DE USUARIOS (Samba)")
    menu_usuarios.agregar_opcion("Listar usuarios actuales (pdbedit)", AccionBash("Usuarios Registrados", cmd_listar_samba))
    menu_usuarios.agregar_opcion("Añadir un nuevo usuario (smbpasswd)", AccionPython("Añadir Usuario", agregar_usuario_samba))
    menu_usuarios.agregar_opcion("Eliminar un usuario (smbpasswd)", AccionPython("Eliminar Usuario", eliminar_usuario_samba))

    # --- Submenú: Administración de Permisos ---
    menu_permisos = Menu("CONTROL DE PERMISOS DE CARPETAS")
    menu_permisos.agregar_opcion("Cambiar propietario y grupo (chown)", AccionPython("Cambiar Propietario", cambiar_propietario_carpeta))
    menu_permisos.agregar_opcion("Cambiar permisos de lectura/escritura (chmod)", AccionPython("Cambiar Permisos", cambiar_permisos_carpeta))

    # --- Submenú: Control de Servicio Samba ---
    menu_servicio = Menu("CONTROL DE SERVICIO (smbd)")
    menu_servicio.agregar_opcion("Ver estado del servicio", AccionBash("Estado del Servicio", cmd_estado_samba))
    menu_servicio.agregar_opcion("Reiniciar Samba (Aplicar cambios de smb.conf)", AccionPython("Reinicio Seguro", reiniciar_servicio_samba))

    # --- Menú Principal ---
    menu_principal = Menu("SISTEMA DE ADMINISTRACIÓN V1.0.0 (by N0kyapi)")
    menu_principal.agregar_opcion("Monitorización de Recursos (CPU, RAM, Disco)", AccionBash("Recursos del Sistema", cmd_recursos))
    menu_principal.agregar_opcion("Monitorización de Conexiones Samba (smbstatus)", AccionBash("Conexiones Activas", "sudo smbstatus"))
    menu_principal.agregar_opcion("Administración de Accesos (Crear/Eliminar Usuarios)", menu_usuarios)
    menu_principal.agregar_opcion("Administración de Permisos de Directorios", menu_permisos)
    menu_principal.agregar_opcion("Estado y Control del Servicio Samba", menu_servicio)

    # Iniciar la TUI
    app = AplicacionTUI(stdscr, menu_principal)
    app.ejecutar()

if __name__ == "__main__":
    curses.wrapper(main)