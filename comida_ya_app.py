"""
APLICACIÓN MÓVIL "COMIDA YA"
Sistema completo de pedidos de comida en línea
Desarrollado con Python + Tkinter + MySQL
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import hashlib
from PIL import Image, ImageTk
import io

# =====================================================
# CONFIGURACIÓN DE BASE DE DATOS
# =====================================================

class Database:
    def __init__(self):
        self.host = 'localhost'
        self.database = 'comida_ya'
        self.user = 'root'
        self.password = 'Nv36+nogales'  # Cambia esto por tu contraseña de MySQL
    def connect(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return connection
        except Error as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos:\n{e}")
            return None
    
    def execute_query(self, query, params=None):
        connection = self.connect()
        if connection is None:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT') or query.strip().upper().startswith('CALL'):
                result = cursor.fetchall()
            else:
                connection.commit()
                result = cursor.lastrowid
            
            cursor.close()
            connection.close()
            return result
        except Error as e:
            messagebox.showerror("Error", f"Error en la consulta:\n{e}")
            return None
    
    def call_procedure(self, procedure_name, params):
        connection = self.connect()
        if connection is None:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.callproc(procedure_name, params)
            
            results = []
            for result in cursor.stored_results():
                results.extend(result.fetchall())
            
            connection.commit()
            cursor.close()
            connection.close()
            return results
        except Error as e:
            messagebox.showerror("Error", f"Error al ejecutar procedimiento:\n{e}")
            return None

# =====================================================
# VENTANA PRINCIPAL DE LA APLICACIÓN
# =====================================================

class ComidaYaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Comida Ya - Pedidos en Línea")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f5f5f5')
        
        self.db = Database()
        self.usuario_actual = None
        self.carrito = []
        self.pedido_actual = None
        
        # Colores del diseño
        self.color_primario = "#5B4CFF"
        self.color_secundario = "#FF4C4C"
        self.color_verde = "#00C896"
        self.color_fondo = "#f5f5f5"
        self.color_blanco = "#FFFFFF"
        
        # Verificar conexión antes de mostrar login
        if self.verificar_conexion():
            self.mostrar_login()
        else:
            self.mostrar_error_conexion()
    
    def verificar_conexion(self):
        """Verifica si la conexión a la base de datos funciona"""
        try:
            conn = self.db.connect()
            if conn:
                conn.close()
                return True
            return False
        except:
            return False
    
    def mostrar_error_conexion(self):
        """Muestra un mensaje de error si no hay conexión"""
        error_frame = tk.Frame(self.root, bg=self.color_fondo)
        error_frame.pack(expand=True)
        
        tk.Label(error_frame, text="❌", font=('Arial', 60), 
                bg=self.color_fondo, fg=self.color_secundario).pack(pady=20)
        
        tk.Label(error_frame, text="Error de Conexión", 
                font=('Arial', 24, 'bold'), bg=self.color_fondo).pack(pady=10)
        
        mensaje = """No se pudo conectar a la base de datos.

Verifica que:
1. MySQL esté corriendo
2. La base de datos 'comida_ya' exista
3. Las credenciales en el código sean correctas
4. El usuario y contraseña de MySQL sean correctos

Configuración actual:
Host: localhost
Database: comida_ya
User: root"""
        
        tk.Label(error_frame, text=mensaje, font=('Arial', 11), 
                bg=self.color_fondo, fg='gray', justify='left').pack(pady=20)
        
        tk.Button(error_frame, text="🔄 Reintentar", font=('Arial', 12, 'bold'), 
                 bg=self.color_primario, fg='white', cursor='hand2',
                 command=self.reintentar_conexion).pack(pady=20)
    
    def reintentar_conexion(self):
        """Reintenta la conexión"""
        self.limpiar_ventana()
        if self.verificar_conexion():
            self.mostrar_login()
        else:
            self.mostrar_error_conexion()
    
    # =====================================================
    # INTERFAZ 1: LOGIN / REGISTRO
    # =====================================================
    
    def mostrar_login(self):
        self.limpiar_ventana()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.color_fondo)
        main_frame.pack(expand=True, fill='both', padx=50, pady=50)
        
        # Lado izquierdo - Login
        login_frame = tk.Frame(main_frame, bg=self.color_blanco, relief='raised', bd=2)
        login_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        # Logo y título
        tk.Label(login_frame, text="🍽️ Comida Ya + Acceso", font=('Arial', 16, 'bold'), 
                bg=self.color_blanco, fg=self.color_primario).pack(pady=20)
        
        tk.Label(login_frame, text="Inicia sesión", font=('Arial', 20, 'bold'), 
                bg=self.color_blanco).pack(pady=10)
        
        tk.Label(login_frame, text="Accede con correo o teléfono, o continúa con Google", 
                font=('Arial', 10), bg=self.color_blanco, fg='gray').pack()
        
        # Campos de login
        tk.Label(login_frame, text="Correo o teléfono", font=('Arial', 10, 'bold'), 
                bg=self.color_blanco).pack(pady=(30, 5), anchor='w', padx=50)
        
        self.login_email = tk.Entry(login_frame, font=('Arial', 12), width=30)
        self.login_email.pack(pady=5, padx=50)
        
        tk.Label(login_frame, text="Contraseña", font=('Arial', 10, 'bold'), 
                bg=self.color_blanco).pack(pady=(20, 5), anchor='w', padx=50)
        
        self.login_password = tk.Entry(login_frame, font=('Arial', 12), width=30, show='*')
        self.login_password.pack(pady=5, padx=50)
        
        tk.Button(login_frame, text="Entrar", font=('Arial', 12, 'bold'), 
                 bg=self.color_primario, fg='white', width=25, cursor='hand2',
                 command=self.realizar_login).pack(pady=20, padx=50)
        
        tk.Button(login_frame, text="🔍 Entrar con Google", font=('Arial', 11), 
                 bg='#f0f0f0', width=25, cursor='hand2').pack(pady=5, padx=50)
        
        # Lado derecho - Registro
        registro_frame = tk.Frame(main_frame, bg=self.color_blanco, relief='raised', bd=2)
        registro_frame.pack(side='right', fill='both', expand=True, padx=10)
        
        tk.Label(registro_frame, text="Crea tu cuenta", font=('Arial', 20, 'bold'), 
                bg=self.color_blanco).pack(pady=20)
        
        tk.Label(registro_frame, text="Pide rápido y seguro. Usa correo o teléfono", 
                font=('Arial', 10), bg=self.color_blanco, fg='gray').pack()
        
        # Campos de registro
        tk.Label(registro_frame, text="Nombre completo", font=('Arial', 10, 'bold'), 
                bg=self.color_blanco).pack(pady=(20, 5), anchor='w', padx=50)
        self.reg_nombre = tk.Entry(registro_frame, font=('Arial', 12), width=30)
        self.reg_nombre.pack(pady=5, padx=50)
        
        tk.Label(registro_frame, text="Apellido", font=('Arial', 10, 'bold'), 
                bg=self.color_blanco).pack(pady=(10, 5), anchor='w', padx=50)
        self.reg_apellido = tk.Entry(registro_frame, font=('Arial', 12), width=30)
        self.reg_apellido.pack(pady=5, padx=50)
        
        tk.Label(registro_frame, text="Correo electrónico", font=('Arial', 10, 'bold'), 
                bg=self.color_blanco).pack(pady=(10, 5), anchor='w', padx=50)
        self.reg_email = tk.Entry(registro_frame, font=('Arial', 12), width=30)
        self.reg_email.pack(pady=5, padx=50)
        
        tk.Label(registro_frame, text="Teléfono", font=('Arial', 10, 'bold'), 
                bg=self.color_blanco).pack(pady=(10, 5), anchor='w', padx=50)
        self.reg_telefono = tk.Entry(registro_frame, font=('Arial', 12), width=30)
        self.reg_telefono.pack(pady=5, padx=50)
        
        tk.Label(registro_frame, text="Contraseña", font=('Arial', 10, 'bold'), 
                bg=self.color_blanco).pack(pady=(10, 5), anchor='w', padx=50)
        self.reg_password = tk.Entry(registro_frame, font=('Arial', 12), width=30, show='*')
        self.reg_password.pack(pady=5, padx=50)
        
        tk.Button(registro_frame, text="Registrarme", font=('Arial', 12, 'bold'), 
                 bg=self.color_primario, fg='white', width=25, cursor='hand2',
                 command=self.realizar_registro).pack(pady=20, padx=50)
    
    def realizar_login(self):
        email = self.login_email.get().strip()
        password = self.login_password.get().strip()
        
        if not email or not password:
            messagebox.showwarning("Campos vacíos", "Por favor completa todos los campos")
            return
        
        try:
            # Consulta directa en lugar de procedimiento
            query = """
                SELECT id_usuario, nombre, apellido, email, telefono, rol 
                FROM usuarios 
                WHERE email = %s AND contrasena = %s AND activo = TRUE
            """
            result = self.db.execute_query(query, (email, password))
            
            if result and len(result) > 0:
                self.usuario_actual = result[0]
                
                # Actualizar último acceso
                self.db.execute_query(
                    "UPDATE usuarios SET ultimo_acceso = NOW() WHERE id_usuario = %s",
                    (self.usuario_actual['id_usuario'],)
                )
                
                messagebox.showinfo("Bienvenido", f"¡Hola {self.usuario_actual['nombre']}!")
                
                # Redirigir según rol
                if self.usuario_actual['rol'] == 'Administrador':
                    self.mostrar_panel_admin()
                elif self.usuario_actual['rol'] == 'Empleado':
                    self.mostrar_panel_empleado()
                else:
                    self.mostrar_menu_cliente()
            else:
                messagebox.showerror("Error", "Credenciales incorrectas o usuario inactivo")
                
        except Exception as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar:\n{str(e)}\n\nVerifica que MySQL esté corriendo y la base de datos 'comida_ya' exista.")
    
    def realizar_registro(self):
        nombre = self.reg_nombre.get().strip()
        apellido = self.reg_apellido.get().strip()
        email = self.reg_email.get().strip()
        telefono = self.reg_telefono.get().strip()
        password = self.reg_password.get().strip()
        
        if not all([nombre, apellido, email, telefono, password]):
            messagebox.showwarning("Campos vacíos", "Por favor completa todos los campos")
            return
        
        try:
            # Verificar si el email ya existe
            check = self.db.execute_query(
                "SELECT COUNT(*) as total FROM usuarios WHERE email = %s", 
                (email,)
            )
            
            if check and check[0]['total'] > 0:
                messagebox.showerror("Error", "Este correo ya está registrado")
                return
            
            # Insertar nuevo usuario
            query = """
                INSERT INTO usuarios (nombre, apellido, email, telefono, contrasena, rol)
                VALUES (%s, %s, %s, %s, %s, 'Cliente')
            """
            
            self.db.execute_query(query, (nombre, apellido, email, telefono, password))
            
            messagebox.showinfo("Éxito", "¡Usuario registrado exitosamente!\nAhora puedes iniciar sesión")
            
            # Limpiar campos
            self.reg_nombre.delete(0, 'end')
            self.reg_apellido.delete(0, 'end')
            self.reg_email.delete(0, 'end')
            self.reg_telefono.delete(0, 'end')
            self.reg_password.delete(0, 'end')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar:\n{str(e)}")
    
    # =====================================================
    # INTERFAZ 2: MENÚ PARA CLIENTES
    # =====================================================
    
    def mostrar_menu_cliente(self):
        self.limpiar_ventana()
        
        # Header
        header = tk.Frame(self.root, bg=self.color_primario, height=80)
        header.pack(fill='x')
        
        tk.Label(header, text=f"🍽️ Comida Ya - ¡Hola {self.usuario_actual['nombre']}!", 
                font=('Arial', 18, 'bold'), bg=self.color_primario, fg='white').pack(side='left', padx=20, pady=20)
        
        tk.Button(header, text=f"🛒 Carrito ({len(self.carrito)})", 
                 font=('Arial', 12, 'bold'), bg='white', fg=self.color_primario, 
                 cursor='hand2', command=self.mostrar_carrito).pack(side='right', padx=20, pady=20)
        
        tk.Button(header, text="📋 Mis Pedidos", font=('Arial', 12), 
                 bg='white', fg=self.color_primario, cursor='hand2',
                 command=self.mostrar_mis_pedidos).pack(side='right', padx=5, pady=20)
        
        tk.Button(header, text="🚪 Salir", font=('Arial', 12), 
                 bg='white', fg=self.color_primario, cursor='hand2',
                 command=self.cerrar_sesion).pack(side='right', padx=5, pady=20)
        
        # Contenedor principal con scroll
        main_container = tk.Frame(self.root, bg=self.color_fondo)
        main_container.pack(fill='both', expand=True)
        
        # Canvas principal
        canvas = tk.Canvas(main_container, bg=self.color_fondo)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.color_fondo)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Búsqueda
        search_frame = tk.Frame(scrollable_frame, bg=self.color_blanco, relief='raised', bd=1)
        search_frame.pack(fill='x', pady=20, padx=20)
        
        tk.Label(search_frame, text="🔍", font=('Arial', 16), bg=self.color_blanco).pack(side='left', padx=10)
        search_entry = tk.Entry(search_frame, font=('Arial', 12), relief='flat')
        search_entry.pack(side='left', fill='x', expand=True, pady=10, padx=5)
        
        # Categorías
        categorias_frame = tk.Frame(scrollable_frame, bg=self.color_fondo)
        categorias_frame.pack(fill='x', pady=(0, 20), padx=20)
        
        tk.Label(categorias_frame, text="Categorías:", font=('Arial', 12, 'bold'), 
                bg=self.color_fondo).pack(side='left', padx=10)
        
        try:
            categorias = self.db.execute_query("SELECT * FROM categorias WHERE activo = TRUE ORDER BY orden")
            
            tk.Button(categorias_frame, text="📋 Todo", font=('Arial', 11, 'bold'), 
                     bg=self.color_primario, fg='white', cursor='hand2').pack(side='left', padx=5)
            
            if categorias:
                for cat in categorias:
                    tk.Button(categorias_frame, text=f"{cat['icono']} {cat['nombre']}", 
                             font=('Arial', 11), bg='white', cursor='hand2').pack(side='left', padx=5)
        except Exception as e:
            print(f"Error al cargar categorías: {e}")
        
        # Grid de productos
        productos_frame = tk.Frame(scrollable_frame, bg=self.color_fondo)
        productos_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        try:
            productos = self.db.execute_query("SELECT * FROM v_menu_disponible")
            
            if productos:
                row, col = 0, 0
                for producto in productos:
                    self.crear_tarjeta_producto(productos_frame, producto, row, col)
                    col += 1
                    if col > 2:
                        col = 0
                        row += 1
            else:
                tk.Label(productos_frame, text="No hay productos disponibles", 
                        font=('Arial', 14), bg=self.color_fondo, fg='gray').pack(pady=50)
                
        except Exception as e:
            tk.Label(productos_frame, text=f"Error al cargar productos:\n{str(e)}", 
                    font=('Arial', 12), bg=self.color_fondo, fg='red').pack(pady=50)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Hacer que funcione el scroll con la rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def crear_tarjeta_producto(self, parent, producto, row, col):
        card = tk.Frame(parent, bg=self.color_blanco, relief='raised', bd=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        # Emoji del producto
        tk.Label(card, text=producto.get('icono_categoria', '🍽️'), 
                font=('Arial', 40), bg=self.color_blanco).pack(pady=10)
        
        # Nombre
        tk.Label(card, text=producto['nombre'], font=('Arial', 14, 'bold'), 
                bg=self.color_blanco).pack(pady=5)
        
        # Descripción
        desc = producto.get('descripcion', '')[:60] + '...' if len(producto.get('descripcion', '')) > 60 else producto.get('descripcion', '')
        tk.Label(card, text=desc, font=('Arial', 9), bg=self.color_blanco, 
                fg='gray', wraplength=200).pack(pady=5)
        
        # Precio
        tk.Label(card, text=f"${producto['precio']:.2f}", 
                font=('Arial', 16, 'bold'), bg=self.color_blanco, 
                fg=self.color_verde).pack(pady=5)
        
        # Botón agregar
        tk.Button(card, text="➕ Agregar", font=('Arial', 11, 'bold'), 
                 bg=self.color_primario, fg='white', cursor='hand2',
                 command=lambda p=producto: self.agregar_al_carrito(p)).pack(pady=10, padx=20, fill='x')
    
    def filtrar_productos(self, id_categoria):
        if id_categoria:
            productos = self.db.execute_query(
                "SELECT * FROM v_menu_disponible WHERE id_categoria = %s", 
                (id_categoria,)
            )
        else:
            productos = self.db.execute_query("SELECT * FROM v_menu_disponible")
        
        # Refrescar la vista
        self.mostrar_menu_cliente()
    
    def agregar_al_carrito(self, producto):
        # Verificar si ya está en el carrito
        for item in self.carrito:
            if item['id_producto'] == producto['id_producto']:
                item['cantidad'] += 1
                messagebox.showinfo("Carrito", f"Cantidad actualizada: {item['cantidad']}")
                return
        
        # Agregar nuevo producto
        self.carrito.append({
            'id_producto': producto['id_producto'],
            'nombre': producto['nombre'],
            'precio': producto['precio'],
            'cantidad': 1
        })
        
        messagebox.showinfo("Carrito", f"{producto['nombre']} agregado al carrito")
        self.mostrar_menu_cliente()  # Refrescar para actualizar contador
    
    # =====================================================
    # INTERFAZ 3: CARRITO DE COMPRAS
    # =====================================================
    
    def mostrar_carrito(self):
        if not self.carrito:
            messagebox.showinfo("Carrito vacío", "No hay productos en el carrito")
            return
        
        carrito_window = tk.Toplevel(self.root)
        carrito_window.title("Confirmar pedido")
        carrito_window.geometry("600x700")
        carrito_window.configure(bg=self.color_fondo)
        
        # Header
        header = tk.Frame(carrito_window, bg=self.color_primario)
        header.pack(fill='x')
        tk.Label(header, text="🛒 Confirmar pedido", font=('Arial', 16, 'bold'), 
                bg=self.color_primario, fg='white').pack(pady=15)
        
        # Contenido con scroll
        canvas = tk.Canvas(carrito_window, bg=self.color_fondo)
        scrollbar = ttk.Scrollbar(carrito_window, orient="vertical", command=canvas.yview)
        content_frame = tk.Frame(canvas, bg=self.color_fondo)
        
        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Productos en el carrito
        tk.Label(content_frame, text="📦 Productos en tu carrito", 
                font=('Arial', 12, 'bold'), bg=self.color_fondo).pack(pady=10, anchor='w', padx=20)
        
        for item in self.carrito:
            item_frame = tk.Frame(content_frame, bg=self.color_blanco, relief='raised', bd=1)
            item_frame.pack(fill='x', padx=20, pady=5)
            
            tk.Label(item_frame, text=item['nombre'], font=('Arial', 11, 'bold'), 
                    bg=self.color_blanco).pack(side='left', padx=10, pady=10)
            
            tk.Label(item_frame, text=f"${item['precio']:.2f}", font=('Arial', 11), 
                    bg=self.color_blanco, fg=self.color_verde).pack(side='right', padx=10)
            
            tk.Label(item_frame, text=f"x{item['cantidad']}", font=('Arial', 11), 
                    bg=self.color_blanco).pack(side='right', padx=5)
        
        # Resumen
        resumen_frame = tk.Frame(content_frame, bg=self.color_blanco, relief='raised', bd=2)
        resumen_frame.pack(fill='x', padx=20, pady=20)
        
        subtotal = sum(item['precio'] * item['cantidad'] for item in self.carrito)
        impuestos = subtotal * 0.19
        envio = 6.00
        total = subtotal + impuestos + envio
        
        tk.Label(resumen_frame, text="Resumen", font=('Arial', 14, 'bold'), 
                bg=self.color_blanco).pack(pady=10)
        
        tk.Label(resumen_frame, text=f"Subtotal: ${subtotal:.2f}", 
                font=('Arial', 11), bg=self.color_blanco).pack(anchor='w', padx=20, pady=2)
        tk.Label(resumen_frame, text=f"Impuestos (19%): ${impuestos:.2f}", 
                font=('Arial', 11), bg=self.color_blanco).pack(anchor='w', padx=20, pady=2)
        tk.Label(resumen_frame, text=f"Envío: ${envio:.2f}", 
                font=('Arial', 11), bg=self.color_blanco).pack(anchor='w', padx=20, pady=2)
        
        tk.Label(resumen_frame, text=f"Total: ${total:.2f}", 
                font=('Arial', 14, 'bold'), bg=self.color_blanco, 
                fg=self.color_primario).pack(pady=10)
        
        # Botones
        buttons_frame = tk.Frame(content_frame, bg=self.color_fondo)
        buttons_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Button(buttons_frame, text="❌ Cancelar", font=('Arial', 12), 
                 bg='#cccccc', cursor='hand2',
                 command=carrito_window.destroy).pack(side='left', expand=True, fill='x', padx=5)
        
        tk.Button(buttons_frame, text="✓ Confirmar", font=('Arial', 12, 'bold'), 
                 bg=self.color_verde, fg='white', cursor='hand2',
                 command=lambda: self.confirmar_pedido(carrito_window)).pack(side='right', expand=True, fill='x', padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def confirmar_pedido(self, window):
        # Crear el pedido
        result = self.db.call_procedure('sp_crear_pedido', 
                                       [self.usuario_actual['id_usuario'], 1, 1, ''])
        
        if result:
            id_pedido = result[0]['id_pedido']
            
            # Agregar productos
            for item in self.carrito:
                self.db.call_procedure('sp_agregar_producto', 
                                     [id_pedido, item['id_producto'], item['cantidad'], ''])
            
            messagebox.showinfo("Éxito", f"Pedido confirmado!\nCódigo: {result[0]['codigo_pedido']}")
            self.carrito = []
            window.destroy()
            self.mostrar_menu_cliente()
    
    # =====================================================
    # INTERFAZ 4: MIS PEDIDOS (HISTORIAL)
    # =====================================================
    
    def mostrar_mis_pedidos(self):
        self.limpiar_ventana()
        
        # Header
        header = tk.Frame(self.root, bg=self.color_primario, height=80)
        header.pack(fill='x')
        
        tk.Label(header, text="📋 Historial de pedidos", 
                font=('Arial', 18, 'bold'), bg=self.color_primario, fg='white').pack(side='left', padx=20, pady=20)
        
        tk.Button(header, text="⬅ Volver al Menú", font=('Arial', 12), 
                 bg='white', fg=self.color_primario, cursor='hand2',
                 command=self.mostrar_menu_cliente).pack(side='right', padx=20, pady=20)
        
        # Contenedor principal
        main_container = tk.Frame(self.root, bg=self.color_fondo)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Obtener pedidos
        pedidos = self.db.call_procedure('sp_mis_pedidos', [self.usuario_actual['id_usuario']])
        
        if not pedidos:
            tk.Label(main_container, text="No tienes pedidos aún", 
                    font=('Arial', 14), bg=self.color_fondo, fg='gray').pack(pady=50)
            return
        
        # Lista de pedidos
        for pedido in pedidos:
            self.crear_tarjeta_pedido(main_container, pedido)
    
    def crear_tarjeta_pedido(self, parent, pedido):
        card = tk.Frame(parent, bg=self.color_blanco, relief='raised', bd=2)
        card.pack(fill='x', pady=10)
        
        # Header del pedido
        header = tk.Frame(card, bg=self.color_fondo)
        header.pack(fill='x', padx=15, pady=10)
        
        tk.Label(header, text=pedido['codigo_pedido'], 
                font=('Arial', 12, 'bold'), bg=self.color_fondo).pack(side='left')
        
        # Estado con color
        color_estado = pedido.get('color', 'gray')
        tk.Label(header, text=pedido['estado'], 
                font=('Arial', 11, 'bold'), bg=color_estado, fg='white', 
                padx=10, pady=2).pack(side='right')
        
        # Información
        info_frame = tk.Frame(card, bg=self.color_blanco)
        info_frame.pack(fill='x', padx=15, pady=5)
        
        tk.Label(info_frame, text=f"🕒 {pedido['fecha_pedido']}", 
                font=('Arial', 10), bg=self.color_blanco).pack(side='left')
        
        tk.Label(info_frame, text=f"💵 ${pedido['total']:.2f}", 
                font=('Arial', 12, 'bold'), bg=self.color_blanco, 
                fg=self.color_verde).pack(side='right')
        
        # Productos
        productos_text = pedido.get('productos', 'Sin productos')
        tk.Label(card, text=productos_text, font=('Arial', 9), 
                bg=self.color_blanco, fg='gray', wraplength=1000).pack(anchor='w', padx=15, pady=5)
    
    # =====================================================
    # INTERFAZ 5: PANEL DE ADMINISTRACIÓN
    # =====================================================
    
    def mostrar_panel_admin(self):
        self.limpiar_ventana()
        
        # Header
        header = tk.Frame(self.root, bg=self.color_primario, height=80)
        header.pack(fill='x')
        
        tk.Label(header, text="⚙️ Panel de Administración", 
                font=('Arial', 18, 'bold'), bg=self.color_primario, fg='white').pack(side='left', padx=20, pady=20)
        
        tk.Button(header, text="🚪 Cerrar Sesión", font=('Arial', 12), 
                 bg='white', fg=self.color_primario, cursor='hand2',
                 command=self.mostrar_login).pack(side='right', padx=20, pady=20)
        
        # Menú lateral
        sidebar = tk.Frame(self.root, bg=self.color_blanco, width=250, relief='raised', bd=2)
        sidebar.pack(side='left', fill='y')
        
        tk.Label(sidebar, text="Navegación", font=('Arial', 14, 'bold'), 
                bg=self.color_blanco).pack(pady=20)
        
        opciones = [
            ("🏠 Inicio", None),
            ("📦 Pedidos", self.admin_ver_pedidos),
            ("📋 Menú", self.admin_gestionar_menu),
            ("👥 Clientes", self.admin_ver_clientes),
            ("👔 Roles y permisos", None),
            ("⚙️ Configuración", None)
        ]
        
        for texto, comando in opciones:
            btn = tk.Button(sidebar, text=texto, font=('Arial', 11), 
                          bg=self.color_blanco, anchor='w', cursor='hand2',
                          relief='flat', command=comando if comando else None)
            btn.pack(fill='x', padx=10, pady=5)
        
        # Contenido principal
        content = tk.Frame(self.root, bg=self.color_fondo)
        content.pack(side='right', fill='both', expand=True, padx=20, pady=20)
        
        # Estadísticas
        stats_frame = tk.Frame(content, bg=self.color_fondo)
        stats_frame.pack(fill='x', pady=10)
        
        stats = [
            ("Total Pedidos Hoy", "24", self.color_primario),
            ("En Preparación", "8", self.color_secundario),
            ("Ventas del Día", "$1,245", self.color_verde)
        ]
        
        for titulo, valor, color in stats:
            card = tk.Frame(stats_frame, bg=self.color_blanco, relief='raised', bd=2)
            card.pack(side='left', expand=True, fill='both', padx=10)
            
            tk.Label(card, text=titulo, font=('Arial', 11), 
                    bg=self.color_blanco, fg='gray').pack(pady=(15, 5))
            tk.Label(card, text=valor, font=('Arial', 24, 'bold'), 
                    bg=self.color_blanco, fg=color).pack(pady=(5, 15))
        
        # Pedidos recientes
        tk.Label(content, text="📦 Pedidos Recientes", 
                font=('Arial', 14, 'bold'), bg=self.color_fondo).pack(anchor='w', pady=(20, 10))
        
        pedidos = self.db.execute_query(
            "SELECT * FROM v_historial_completo LIMIT 10"
        )
        
        if pedidos:
            for pedido in pedidos:
                self.crear_tarjeta_pedido(content, pedido)
    
    def admin_ver_pedidos(self):
        # Implementar vista de gestión de pedidos
        messagebox.showinfo("Info", "Vista de gestión de pedidos")
    
    def admin_gestionar_menu(self):
        # Ventana para gestionar productos
        menu_window = tk.Toplevel(self.root)
        menu_window.title("Gestión de Menú")
        menu_window.geometry("900x600")
        menu_window.configure(bg=self.color_fondo)
        
        # Header
        header = tk.Frame(menu_window, bg=self.color_primario)
        header.pack(fill='x')
        tk.Label(header, text="📋 Gestión de Menú", font=('Arial', 16, 'bold'), 
                bg=self.color_primario, fg='white').pack(pady=15)
        
        # Botón agregar producto
        tk.Button(menu_window, text="➕ Agregar Producto", font=('Arial', 12, 'bold'), 
                 bg=self.color_verde, fg='white', cursor='hand2',
                 command=self.admin_agregar_producto).pack(pady=10)
        
        # Treeview con productos
        tree_frame = tk.Frame(menu_window)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('ID', 'Código', 'Nombre', 'Categoría', 'Precio', 'Disponible')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Cargar productos
        productos = self.db.execute_query("SELECT * FROM productos")
        for prod in productos:
            tree.insert('', 'end', values=(
                prod['id_producto'],
                prod['codigo'],
                prod['nombre'],
                prod['id_categoria'],
                f"${prod['precio']:.2f}",
                'Sí' if prod['disponible'] else 'No'
            ))
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def admin_agregar_producto(self):
        # Ventana para agregar producto
        add_window = tk.Toplevel(self.root)
        add_window.title("Agregar Producto")
        add_window.geometry("500x600")
        add_window.configure(bg=self.color_blanco)
        
        tk.Label(add_window, text="Agregar / Editar producto", 
                font=('Arial', 16, 'bold'), bg=self.color_blanco).pack(pady=20)
        
        # Campos
        campos = [
            ("Código del producto:", 'codigo'),
            ("Nombre del producto:", 'nombre'),
            ("Descripción:", 'descripcion'),
            ("Ingredientes:", 'ingredientes'),
            ("Precio:", 'precio'),
            ("Categoría ID:", 'categoria'),
            ("Tiempo de preparación (min):", 'tiempo')
        ]
        
        entries = {}
        for label, key in campos:
            frame = tk.Frame(add_window, bg=self.color_blanco)
            frame.pack(fill='x', padx=40, pady=5)
            
            tk.Label(frame, text=label, font=('Arial', 10, 'bold'), 
                    bg=self.color_blanco).pack(anchor='w')
            
            if key == 'descripcion' or key == 'ingredientes':
                entry = tk.Text(frame, height=3, font=('Arial', 10))
            else:
                entry = tk.Entry(frame, font=('Arial', 10))
            
            entry.pack(fill='x', pady=2)
            entries[key] = entry
        
        # Botones
        btn_frame = tk.Frame(add_window, bg=self.color_blanco)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="💾 Guardar", font=('Arial', 12, 'bold'), 
                 bg=self.color_verde, fg='white', cursor='hand2',
                 command=lambda: self.guardar_producto(entries, add_window)).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="❌ Cancelar", font=('Arial', 12), 
                 bg='#cccccc', cursor='hand2',
                 command=add_window.destroy).pack(side='left', padx=10)
    
    def guardar_producto(self, entries, window):
        try:
            codigo = entries['codigo'].get()
            nombre = entries['nombre'].get()
            descripcion = entries['descripcion'].get('1.0', 'end-1c')
            ingredientes = entries['ingredientes'].get('1.0', 'end-1c')
            precio = float(entries['precio'].get())
            categoria = int(entries['categoria'].get())
            tiempo = int(entries['tiempo'].get())
            
            query = """
                INSERT INTO productos (codigo, nombre, descripcion, ingredientes, precio, 
                                     id_categoria, tiempo_preparacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            self.db.execute_query(query, (codigo, nombre, descripcion, ingredientes, 
                                        precio, categoria, tiempo))
            
            messagebox.showinfo("Éxito", "Producto guardado correctamente")
            window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {e}")
    
    def admin_ver_clientes(self):
        # Ventana de clientes
        clientes_window = tk.Toplevel(self.root)
        clientes_window.title("Gestión de Clientes")
        clientes_window.geometry("900x600")
        clientes_window.configure(bg=self.color_fondo)
        
        # Header
        header = tk.Frame(clientes_window, bg=self.color_primario)
        header.pack(fill='x')
        tk.Label(header, text="👥 Gestión de Clientes", font=('Arial', 16, 'bold'), 
                bg=self.color_primario, fg='white').pack(pady=15)
        
        # Treeview
        tree_frame = tk.Frame(clientes_window)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        columns = ('ID', 'Nombre', 'Email', 'Teléfono', 'Rol', 'Activo')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Cargar clientes
        clientes = self.db.execute_query("SELECT * FROM usuarios")
        for cliente in clientes:
            tree.insert('', 'end', values=(
                cliente['id_usuario'],
                f"{cliente['nombre']} {cliente['apellido']}",
                cliente['email'],
                cliente['telefono'],
                cliente['rol'],
                'Sí' if cliente['activo'] else 'No'
            ))
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    # =====================================================
    # INTERFAZ 6: PANEL DE EMPLEADO (COCINA)
    # =====================================================
    
    def mostrar_panel_empleado(self):
        self.limpiar_ventana()
        
        # Header
        header = tk.Frame(self.root, bg=self.color_secundario, height=80)
        header.pack(fill='x')
        
        tk.Label(header, text="👨‍🍳 Panel de Cocina", 
                font=('Arial', 18, 'bold'), bg=self.color_secundario, fg='white').pack(side='left', padx=20, pady=20)
        
        tk.Button(header, text="🔄 Actualizar", font=('Arial', 12), 
                 bg='white', fg=self.color_secundario, cursor='hand2',
                 command=self.mostrar_panel_empleado).pack(side='right', padx=5, pady=20)
        
        tk.Button(header, text="🚪 Salir", font=('Arial', 12), 
                 bg='white', fg=self.color_secundario, cursor='hand2',
                 command=self.mostrar_login).pack(side='right', padx=20, pady=20)
        
        # Contenedor principal
        main_container = tk.Frame(self.root, bg=self.color_fondo)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Estados de pedidos
        estados_frame = tk.Frame(main_container, bg=self.color_fondo)
        estados_frame.pack(fill='both', expand=True)
        
        estados = [
            (1, "Pendientes", "yellow"),
            (2, "Confirmados", "blue"),
            (3, "En Preparación", "orange"),
            (4, "Listos", "green")
        ]
        
        for id_estado, nombre, color in estados:
            self.crear_columna_estado(estados_frame, id_estado, nombre, color)
    
    def crear_columna_estado(self, parent, id_estado, nombre, color):
        columna = tk.Frame(parent, bg=self.color_blanco, relief='raised', bd=2)
        columna.pack(side='left', fill='both', expand=True, padx=10)
        
        # Header
        header = tk.Frame(columna, bg=color)
        header.pack(fill='x')
        tk.Label(header, text=nombre, font=('Arial', 14, 'bold'), 
                bg=color, fg='white').pack(pady=10)
        
        # Canvas con scroll
        canvas = tk.Canvas(columna, bg=self.color_blanco)
        scrollbar = ttk.Scrollbar(columna, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=self.color_blanco)
        
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Obtener pedidos por estado
        pedidos = self.db.execute_query(
            "SELECT * FROM v_historial_completo WHERE estado = %s LIMIT 10", 
            (nombre,)
        )
        
        if pedidos:
            for pedido in pedidos:
                self.crear_tarjeta_pedido_cocina(content, pedido, id_estado)
        else:
            tk.Label(content, text="Sin pedidos", font=('Arial', 11), 
                    bg=self.color_blanco, fg='gray').pack(pady=20)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def crear_tarjeta_pedido_cocina(self, parent, pedido, estado_actual):
        card = tk.Frame(parent, bg=self.color_fondo, relief='raised', bd=2)
        card.pack(fill='x', padx=10, pady=5)
        
        tk.Label(card, text=pedido['codigo_pedido'], font=('Arial', 12, 'bold'), 
                bg=self.color_fondo).pack(anchor='w', padx=10, pady=5)
        
        tk.Label(card, text=pedido.get('productos', ''), font=('Arial', 9), 
                bg=self.color_fondo, wraplength=200).pack(anchor='w', padx=10, pady=2)
        
        tk.Label(card, text=f"💵 ${pedido['total']:.2f}", font=('Arial', 10, 'bold'), 
                bg=self.color_fondo, fg=self.color_verde).pack(anchor='w', padx=10, pady=5)
        
        # Botón para cambiar estado
        if estado_actual < 4:
            siguiente_estado = estado_actual + 1
            tk.Button(card, text="➡ Siguiente", font=('Arial', 9, 'bold'), 
                     bg=self.color_primario, fg='white', cursor='hand2',
                     command=lambda: self.cambiar_estado_empleado(
                         pedido['codigo_pedido'], siguiente_estado
                     )).pack(fill='x', padx=10, pady=5)
    
    def cambiar_estado_empleado(self, codigo_pedido, nuevo_estado):
        # Obtener ID del pedido
        pedido = self.db.execute_query(
            "SELECT id_pedido FROM pedidos WHERE codigo_pedido = %s", 
            (codigo_pedido,)
        )
        
        if pedido:
            self.db.call_procedure('sp_cambiar_estado', 
                                 [pedido[0]['id_pedido'], nuevo_estado, 'Actualizado por cocina'])
            messagebox.showinfo("Éxito", f"Estado actualizado para {codigo_pedido}")
            self.mostrar_panel_empleado()
    
    # =====================================================
    # UTILIDADES
    # =====================================================
    
    def limpiar_ventana(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def cerrar_sesion(self):
        self.usuario_actual = None
        self.carrito = []
        self.mostrar_login()

# =====================================================
# EJECUTAR APLICACIÓN
# =====================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = ComidaYaApp(root)
    root.mainloop() 
# =====================================================