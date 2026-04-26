import random
import tkinter as tk
from tkinter import ttk
import threading
from dataclasses import dataclass
from typing import List, Callable


@dataclass(frozen=True)
class Articulo:
    nombre: str
    peso: float
    valor: float

class IndividuoMochila:
    def __init__(self, cromosoma: List[int]):
        self.cromosoma = tuple(cromosoma)
        self._aptitud = None

    def calcular_aptitud(self, articulos: List[Articulo], peso_maximo: float, penalizacion: float) -> float:
        if self._aptitud is not None:
            return self._aptitud

        peso_total = sum(articulo.peso * gen for articulo, gen in zip(articulos, self.cromosoma))
        valor_total = sum(articulo.valor * gen for articulo, gen in zip(articulos, self.cromosoma))

        if peso_total > peso_maximo:
            self._aptitud = max(0.0, valor_total - (penalizacion * (peso_total - peso_maximo)))
        else:
            self._aptitud = valor_total

        return self._aptitud

class AlgoritmoGenetico:
    def __init__(self, tamanio_poblacion: int, tasa_mutacion: float, tasa_cruza: float,
                 tamanio_torneo: int, cantidad_elite: int,
                 funcion_aptitud: Callable[[IndividuoMochila], float]):
        self.tamanio_poblacion = tamanio_poblacion
        self.tasa_mutacion = tasa_mutacion
        self.tasa_cruza = tasa_cruza
        self.tamanio_torneo = tamanio_torneo
        self.cantidad_elite = cantidad_elite
        self.funcion_aptitud = funcion_aptitud
        self.al_terminar_generacion = None

    def _cruzar(self, padre1: IndividuoMochila, padre2: IndividuoMochila) -> IndividuoMochila:
        if random.random() > self.tasa_cruza:
            return IndividuoMochila(list(padre1.cromosoma))
        punto = random.randint(1, len(padre1.cromosoma) - 1)
        cromosoma_hijo = list(padre1.cromosoma[:punto]) + list(padre2.cromosoma[punto:])
        return IndividuoMochila(cromosoma_hijo)

    def _mutar(self, individuo: IndividuoMochila) -> IndividuoMochila:
        cromosoma = list(individuo.cromosoma)
        for i in range(len(cromosoma)):
            if random.random() < self.tasa_mutacion:
                cromosoma[i] = 1 - cromosoma[i]
        return IndividuoMochila(cromosoma)

    def evolucionar(self, poblacion_inicial: List[IndividuoMochila], generaciones: int) -> IndividuoMochila:
        poblacion = poblacion_inicial
        mejor_general = None
        mejor_aptitud = -1.0

        for gen in range(generaciones):
            poblacion_con_aptitud = [(ind, self.funcion_aptitud(ind)) for ind in poblacion]
            poblacion_con_aptitud.sort(key=lambda x: x[1], reverse=True)

            if poblacion_con_aptitud[0][1] > mejor_aptitud:
                mejor_general = poblacion_con_aptitud[0][0]
                mejor_aptitud = poblacion_con_aptitud[0][1]

            if self.al_terminar_generacion:
                self.al_terminar_generacion(gen + 1, generaciones, mejor_aptitud)

            nueva_poblacion = []

            limite_elite = min(self.cantidad_elite, len(poblacion_con_aptitud))
            nueva_poblacion.extend([ind for ind, apt in poblacion_con_aptitud[:limite_elite]])

            while len(nueva_poblacion) < self.tamanio_poblacion:
                p1 = max(random.sample(poblacion_con_aptitud, min(self.tamanio_torneo, len(poblacion_con_aptitud))),
                         key=lambda x: x[1])[0]
                p2 = max(random.sample(poblacion_con_aptitud, min(self.tamanio_torneo, len(poblacion_con_aptitud))),
                         key=lambda x: x[1])[0]

                hijo = self._cruzar(p1, p2)
                hijo = self._mutar(hijo)
                nueva_poblacion.append(hijo)

            poblacion = nueva_poblacion

        return mejor_general


class AplicacionMochila:
    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz
        self.raiz.title("Optimizador de Mochila - Algoritmo Genético")
        self.raiz.geometry("500x800")

        self.articulos = [
            Articulo("Laptop", 2.5, 500), Articulo("Cámara", 1.2, 300), Articulo("Termo", 0.8, 20),
            Articulo("Libro", 1.5, 40), Articulo("Chaqueta", 1.0, 60), Articulo("Botiquín", 0.6, 150),
            Articulo("Linterna", 0.4, 80), Articulo("Batería", 0.5, 90), Articulo("GPS", 0.3, 120),
            Articulo("Cuerda", 1.8, 45), Articulo("Tienda", 3.0, 200), Articulo("Comida", 2.0, 100),
            Articulo("Agua", 2.5, 80), Articulo("Brújula", 0.1, 30), Articulo("Cuchillo", 0.4, 75),
            Articulo("Fósforos", 0.05, 10), Articulo("Manta", 1.2, 50), Articulo("Saco dormir", 1.5, 110),
            Articulo("Prismáticos", 0.9, 140), Articulo("Gafas", 0.1, 40), Articulo("Repelente", 0.2, 25),
            Articulo("Radio", 0.6, 85), Articulo("Cargador Solar", 0.5, 130), Articulo("Botas", 1.4, 95),
        ]
        self.peso_maximo = 12.0

        self._construir_interfaz()

    def _construir_interfaz(self):
        marco = ttk.Frame(self.raiz, padding="10")
        marco.pack(fill=tk.BOTH, expand=True)

        ttk.Label(marco, text="Inventario Disponible", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))

        texto_inventario = " | ".join([f"{art.nombre} ({art.peso}kg, Q{art.valor})" for art in self.articulos])
        caja_inventario = tk.Text(marco, height=3, wrap=tk.WORD, state=tk.NORMAL)
        caja_inventario.insert(tk.END, texto_inventario)
        caja_inventario.config(state=tk.DISABLED)
        caja_inventario.pack(fill=tk.X, pady=(0, 15))

        marco_parametros = ttk.LabelFrame(marco, text="Parámetros del Algoritmo", padding="10")
        marco_parametros.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(marco_parametros, text="Generaciones:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entrada_generaciones = ttk.Entry(marco_parametros, width=10)
        self.entrada_generaciones.insert(0, "50")
        self.entrada_generaciones.grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)

        ttk.Label(marco_parametros, text="Población:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entrada_poblacion = ttk.Entry(marco_parametros, width=10)
        self.entrada_poblacion.insert(0, "20")
        self.entrada_poblacion.grid(row=1, column=1, sticky=tk.W, pady=2, padx=5)

        ttk.Label(marco_parametros, text="Mutación (0.0-1.0):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entrada_mutacion = ttk.Entry(marco_parametros, width=10)
        self.entrada_mutacion.insert(0, "0.05")
        self.entrada_mutacion.grid(row=2, column=1, sticky=tk.W, pady=2, padx=5)

        ttk.Label(marco_parametros, text="Cruza (0.0-1.0):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.entrada_cruza = ttk.Entry(marco_parametros, width=10)
        self.entrada_cruza.insert(0, "0.8")
        self.entrada_cruza.grid(row=3, column=1, sticky=tk.W, pady=2, padx=5)

        ttk.Label(marco_parametros, text="Torneo (Individuos):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.entrada_torneo = ttk.Entry(marco_parametros, width=10)
        self.entrada_torneo.insert(0, "3")
        self.entrada_torneo.grid(row=4, column=1, sticky=tk.W, pady=2, padx=5)

        ttk.Label(marco_parametros, text="Elitismo (Individuos):").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.entrada_elite = ttk.Entry(marco_parametros, width=10)
        self.entrada_elite.insert(0, "2")
        self.entrada_elite.grid(row=5, column=1, sticky=tk.W, pady=2, padx=5)

        ttk.Label(marco_parametros, text="Penalización por kg:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.entrada_penalizacion = ttk.Entry(marco_parametros, width=10)
        self.entrada_penalizacion.insert(0, "800.0")
        self.entrada_penalizacion.grid(row=6, column=1, sticky=tk.W, pady=2, padx=5)

        self.boton_ejecutar = ttk.Button(marco, text="Ejecutar Algoritmo Genético", command=self.iniciar_hilo_algoritmo)
        self.boton_ejecutar.pack(pady=(0, 10))

        self.var_progreso = tk.DoubleVar()
        self.barra_progreso = ttk.Progressbar(marco, variable=self.var_progreso, maximum=100)
        self.barra_progreso.pack(fill=tk.X, pady=(0, 5))

        self.etiqueta_estado = ttk.Label(marco, text="Listo.")
        self.etiqueta_estado.pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(marco, text="Mejor Solución Encontrada", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.texto_resultado = tk.Text(marco, height=12, state=tk.DISABLED)
        self.texto_resultado.pack(fill=tk.BOTH, expand=True)

    def iniciar_hilo_algoritmo(self):
        try:
            generaciones = int(self.entrada_generaciones.get())
            poblacion = int(self.entrada_poblacion.get())
            mutacion = float(self.entrada_mutacion.get())
            cruza = float(self.entrada_cruza.get())
            torneo = int(self.entrada_torneo.get())
            elite = int(self.entrada_elite.get())
            penalizacion = float(self.entrada_penalizacion.get())
        except ValueError:
            self._mostrar_resultado("Error: Verifica que los números y decimales sean válidos.")
            return

        self.boton_ejecutar.config(state=tk.DISABLED)
        self._mostrar_resultado("Calculando...")
        self.var_progreso.set(0)

        hilo = threading.Thread(
            target=self._ejecutar_logica_algoritmo,
            args=(generaciones, poblacion, mutacion, cruza, torneo, elite, penalizacion),
            daemon=True
        )
        hilo.start()

    def _ejecutar_logica_algoritmo(self, generaciones, poblacion, mutacion, cruza, torneo, elite, penalizacion):
        def aptitud_mochila(individuo: IndividuoMochila) -> float:
            return individuo.calcular_aptitud(self.articulos, self.peso_maximo, penalizacion)

        longitud_cromosoma = len(self.articulos)
        poblacion_inicial = [
            IndividuoMochila([random.choice([0, 1]) for _ in range(longitud_cromosoma)])
            for _ in range(poblacion)
        ]

        ag = AlgoritmoGenetico(
            tamanio_poblacion=poblacion,
            tasa_mutacion=mutacion,
            tasa_cruza=cruza,
            tamanio_torneo=torneo,
            cantidad_elite=elite,
            funcion_aptitud=aptitud_mochila
        )

        ag.al_terminar_generacion = self._actualizar_progreso

        mejor_solucion = ag.evolucionar(poblacion_inicial, generaciones)

        self.raiz.after(0, self._formatear_y_mostrar_resultados, mejor_solucion)
        self.raiz.after(0, lambda: self.boton_ejecutar.config(state=tk.NORMAL))
        self.raiz.after(0, lambda: self.etiqueta_estado.config(text="Evolución completada"))

    def _actualizar_progreso(self, generacion_actual: int, total_generaciones: int, mejor_aptitud: float):
        porcentaje_progreso = (generacion_actual / total_generaciones) * 100
        self.raiz.after(0, self.var_progreso.set, porcentaje_progreso)

        texto_estado = f"Generación: {generacion_actual}/{total_generaciones} | Mejor Fitness actual: ${mejor_aptitud:.2f}"
        self.raiz.after(0, lambda: self.etiqueta_estado.config(text=texto_estado))

    def _formatear_y_mostrar_resultados(self, mejor_solucion: IndividuoMochila):
        peso_total, valor_total = 0.0, 0.0
        lineas_resultado = []

        for i, gen in enumerate(mejor_solucion.cromosoma):
            if gen == 1:
                articulo = self.articulos[i]
                lineas_resultado.append(f"{articulo.nombre} (Peso: {articulo.peso}kg, Valor: ${articulo.valor})")
                peso_total += articulo.peso
                valor_total += articulo.valor

        lineas_resultado.append("-" * 30)
        lineas_resultado.append(f"Peso Total:  {peso_total:.2f} kg / {self.peso_maximo} kg")
        lineas_resultado.append(f"Valor Total: Q{valor_total:.2f}")

        if peso_total > self.peso_maximo:
            lineas_resultado.append("\nLa mochila superó el peso máximo (penalizada)")

        self._mostrar_resultado("\n".join(lineas_resultado))

    def _mostrar_resultado(self, mensaje: str):
        self.texto_resultado.config(state=tk.NORMAL)
        self.texto_resultado.delete(1.0, tk.END)
        self.texto_resultado.insert(tk.END, mensaje)
        self.texto_resultado.config(state=tk.DISABLED)


if __name__ == "__main__":
    raiz = tk.Tk()
    aplicacion = AplicacionMochila(raiz)
    raiz.mainloop()