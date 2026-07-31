import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import logica

entCodigo = None
entPeso = None
entFlete = None
varFragil = None
varExpress = None
comboCiudad = None
tablaPaquetes = None

# FUNCIONES DE INTERFAZ Y ESTILOS
def aplicarIcono(ventana):
    # Aplica el ícono a la ventana dada. Al usar el parámetro 'default', los diálogos (messagebox, simpledialog) nuevas ventanas heredarán este ícono automáticamente.  
    try:
        ventana.iconbitmap(default="D:/ander/desktop/univalle/i semestre/proyectoFinal/iconoCaja (2).ico")
    except Exception:
        pass

def aplicarEstilosGlobales(widget_raiz, bg_general="#f4f6f9", fg_texto="#000000", fuente=("Times New Roman", 10)):
    # Recorre recursivamente todos los widgets hijos y aplica un tema general.
    # 1. Configurar los estilos para los widgets modernos de 'ttk' (Treeview)
    estilo = ttk.Style()
    estilo.configure("Treeview", font=fuente, background="#FFFFFF", foreground="black")
    estilo.configure("Treeview.Heading", font=(fuente[0], fuente[1], "bold"))

    # 2. Función recursiva para los widgets clásicos de 'tk'
    def aplicar_recursivo(widget):
        clase = widget.winfo_class()
        
        # Fondos generales (Ventanas, Frames y Toplevels)
        if clase in ('Tk', 'Toplevel', 'Frame', 'Labelframe'):
            try: widget.configure(bg=bg_general)
            except: pass
            if clase == 'Labelframe':
                try: widget.configure(fg=fg_texto, font=(fuente[0], fuente[1], "bold"))
                except: pass
        # Textos y Checkbuttons
        elif clase in ('Label', 'Checkbutton'):
            try: 
                widget.configure(bg=bg_general, fg=fg_texto, font=fuente)
                if clase == 'Checkbutton':
                    widget.configure(selectcolor=bg_general)
            except: pass   
        # Botones (Solo aplicamos la fuente para respetar los colores originales)
        elif clase == 'Button':
            try: widget.configure(font=(fuente[0], fuente[1], "bold"))
            except: pass    
        # Cuadros de entrada de texto
        elif clase in ('Entry', 'Text'):
            try: widget.configure(font=fuente)
            except: pass    
        # Llamar a esta misma función para los "hijos" del widget actual
        for hijo in widget.winfo_children():
            aplicar_recursivo(hijo) 
    # Iniciar el recorrido
    aplicar_recursivo(widget_raiz)

# EVENTOS
def eventoRegistrarPaquete():
    codigo = entCodigo.get().strip()
    pesoTexto = entPeso.get().strip()
    fleteTexto = entFlete.get().strip()
    esFragil = varFragil.get()
    esExpress = varExpress.get()
    ciudad = comboCiudad.get()

    esValido, resultado = logica.validarPaquete(codigo, pesoTexto, fleteTexto, ciudad)
    if esValido == False:
        messagebox.showerror("Error de Entrada", resultado)
        return

    peso, valorFlete = resultado
    filaVisual = logica.registrarPaquete(codigo, peso, valorFlete, esFragil, esExpress, ciudad)

    tablaPaquetes.insert("", tk.END, values=filaVisual)
    limpiarFormulario()
    messagebox.showinfo("Éxito", f"Paquete '{codigo}' registrado con destino a {ciudad}.")

def eventoConsolidarCarga():
    pesoTotal = logica.calcular_peso_total(logica.matrizPaquetes)
    fragiles = logica.contar_paquetes_fragiles(logica.matrizPaquetes)
    express = logica.contar_paquetes_express(logica.matrizPaquetes)
    
    carros_armados, sobrantes = logica.consolidar_manifiesto(logica.matrizPaquetes)

    ventanaConsolidado = tk.Toplevel()
    ventanaConsolidado.title("Consolidado de Carga - EnvíaYa")
    ventanaConsolidado.geometry("600x550")
    
    aplicarIcono(ventanaConsolidado)
    
    info_general = (f"RESUMEN DEL MANIFIESTO\n\n"
                    f"Peso Total Acumulado: {pesoTotal:.2f} kg\n"
                    f"Envíos Prioritarios Express: {express}\n"
                    f"Envíos Prioritarios Frágiles: {fragiles}\n\n"
                    f"HISTORIAL DE SALIDAS")
    
    tk.Label(ventanaConsolidado, text=info_general, justify="center", font=("Arial", 11, "bold")).pack(pady=10, padx=10)
    texto_opciones = tk.Text(ventanaConsolidado, height=20, width=70, font=("Consolas", 10))
    texto_opciones.pack(pady=5, padx=10, fill="both", expand=True)
    texto_opciones.tag_configure("centrado", justify="center")

    if carros_armados == []:
        texto_opciones.insert(tk.END, "Aún no hay combinaciones de paquetes suficientes para armar una salida.\n")
    else:
        texto_carros = logica.formatear_salida_carros(carros_armados, 1)
        texto_opciones.insert(tk.END, texto_carros)
        
    texto_pendientes = logica.formatear_sobrantes(sobrantes)
    texto_opciones.insert(tk.END, texto_pendientes)
    texto_opciones.tag_add("centrado", "1.0", "end")
    texto_opciones.config(state="disabled")   
    # Aplicar el estilo también a esta ventana emergente
    aplicarEstilosGlobales(ventanaConsolidado)

def eventoFiltrarCriticos():
    pesoLimite = simpledialog.askfloat("Filtrar Críticos", "Ingrese el peso límite en kg:")
    if pesoLimite is None:
        return
    codigosCriticos = logica.obtener_paquetes_sobrepeso(logica.matrizPaquetes, pesoLimite)
    if codigosCriticos == []:
        messagebox.showinfo("Filtrar Críticos", "Ningún paquete supera ese peso límite.")
    else:
        listaTexto = "\n".join(codigosCriticos)
        messagebox.showwarning("Paquetes Críticos (sobrepeso)", f"Superan {pesoLimite:.2f} kg:\n\n{listaTexto}")

def limpiarFormulario():
    entCodigo.delete(0, tk.END)
    entPeso.delete(0, tk.END)
    entFlete.delete(0, tk.END)
    varFragil.set(False)
    varExpress.set(False)
    comboCiudad.set("") 

# CONSTRUCCIÓN DE INTERFAZ
def construirInterfaz():
    global entCodigo, entPeso, entFlete, varFragil, varExpress, comboCiudad, tablaPaquetes
    listaCiudades = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena", "Cúcuta", "Bucaramanga", 
                     "Pereira", "Santa Marta", "Ibagué", "Manizales", "Pasto", "Montería", "Villavicencio", 
                     "Tunja", "Florencia", "Popayán", "Valledupar", "Quibdó", "Neiva", "Riohacha", "Armenia", 
                     "Sincelejo"]

    ventana = tk.Tk()
    ventana.title("ENVIA YA")
    
    anchoPantalla = ventana.winfo_screenwidth()
    altoPantalla = ventana.winfo_screenheight()
    anchoVentana = int(anchoPantalla * .98)
    altoVentana = int(altoPantalla * 0.8)
    x = (anchoPantalla - anchoVentana) // 2
    y = (altoPantalla - altoVentana) // 2
    ventana.geometry(f"{anchoVentana}x{altoVentana}+{x}+{y}")
    
    aplicarIcono(ventana)

    FramePrincepal = tk.LabelFrame(ventana)
    FramePrincepal.pack(fill="x", padx=20, pady=10)
    
    frameLogo = tk.Frame(FramePrincepal)
    frameLogo.pack(side="right", fill="both", expand=True, padx=10)
    frameLogo.pack_propagate(False) 

    try:
        imgLogo = tk.PhotoImage(file="D:/ander/desktop/univalle/i semestre/proyectoFinal/logo.png")
        imgLogo = imgLogo.subsample(1,1)
        lblLogo = tk.Label(frameLogo, image=imgLogo)
        lblLogo.image = imgLogo  
        lblLogo.pack(expand=True, anchor="center")
    except Exception as e:
        pass

    frameFormulario = tk.LabelFrame(FramePrincepal, text=" Datos del Paquete ", padx=15, pady=15)
    frameFormulario.pack(side="left", fill="x", padx=20, pady=10)

    tk.Label(frameFormulario, text="Código de Guía:").grid(row=0, column=0, sticky="w", pady=5)
    entCodigo = tk.Entry(frameFormulario, width=20)
    entCodigo.grid(row=0, column=1, pady=5, padx=5)

    tk.Label(frameFormulario, text="Peso (kg):").grid(row=0, column=2, sticky="w", pady=5, padx=(15, 0))
    entPeso = tk.Entry(frameFormulario, width=20)
    entPeso.grid(row=0, column=3, pady=5, padx=5)

    tk.Label(frameFormulario, text="Valor del Flete:").grid(row=0, column=4, sticky="w", pady=5,padx=(15, 0) )
    entFlete = tk.Entry(frameFormulario, width=20)
    entFlete.grid(row=0, column=5, pady=5, padx=5)
    
    tk.Label(frameFormulario, text="Ciudad:").grid(row=1, column=0, sticky="w", pady=5)
    comboCiudad = ttk.Combobox(frameFormulario, values=listaCiudades, state="readonly", width=15)
    comboCiudad.grid(row=1, column=1, sticky="w", pady=5, padx=5)
    comboCiudad.set("") 

    varFragil = tk.BooleanVar()
    tk.Checkbutton(frameFormulario, text="Envío Frágil", variable=varFragil).grid(row=1, column=2, columnspan=2, pady=(10))
    varExpress = tk.BooleanVar()
    tk.Checkbutton(frameFormulario, text="Express", variable=varExpress).grid(row=1, column=4, columnspan=2, pady=(10))

    tk.Button(frameFormulario, text="Registrar Paquete", bg="#6475D4", fg="white", command=eventoRegistrarPaquete).grid(row=2, column=0, columnspan=2, pady=(15, 0), sticky="we")
    tk.Button(frameFormulario, text="Filtrar Críticos", bg="#32abf1", fg="white", command=eventoFiltrarCriticos).grid(row=2, column=2, columnspan=2, padx=(15, 0), pady=(15, 0), sticky="we")
    tk.Button(frameFormulario, text="Consolidar Carga", bg="#06A791", fg="white", command=eventoConsolidarCarga).grid(row=2, column=4, columnspan=2, padx=(15, 0), pady=(15, 0), sticky="we")

    frameTabla = tk.LabelFrame(ventana, text=" Manifiesto de Envíos ", padx=10, pady=10)
    frameTabla.pack(fill="both", expand=True, padx=20, pady=10)

    columnas = ("Código", "Peso", "Valor Flete", "Tipo de Envío" , "Ciudad Destino")
    tablaPaquetes = ttk.Treeview(frameTabla, columns=columnas, show="headings", height=12)

    anchos = [150, 100, 120, 150, 150]
    for i, col in enumerate(columnas):
        tablaPaquetes.heading(col, text=col)
        tablaPaquetes.column(col, width=anchos[i], anchor="center")

    scrollbar = ttk.Scrollbar(frameTabla, orient="vertical", command=tablaPaquetes.yview)
    tablaPaquetes.configure(yscrollcommand=scrollbar.set)

    tablaPaquetes.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Aplicar los estilos globales. Los botones mantendrán su color pero adaptarán la fuente.
    aplicarEstilosGlobales(
        widget_raiz=ventana, 
        bg_general="#DCE3F1",      # Fondo gris clarito
        fg_texto="#000000",        # Texto gris muy oscuro
        fuente=("Verdana", 11)     # Fuente y tamaño general
    )

    return ventana