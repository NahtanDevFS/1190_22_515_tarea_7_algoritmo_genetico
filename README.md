Jonathan David Franco Sosa 1190-22-515 Curso: inteligencia artificial

Tarea: Implementación de algoritmo genético que resuelve el problema de la mochila 0/1 (Knapsack Problem)

Este proyecto es una implementación interactiva en Python que resuelve el clásico Problema de la Mochila 0/1 (Knapsack Problem) utilizando un Algoritmo Genético, 
cuenta con una interfaz gráfica (GUI) hecha con tkinter que permite ajustar los hiperparámetros del motor evolutivo y visualizar el proceso de convergencia.

El programa busca la combinación óptima de objetos de un inventario disponible para maximizar el valor total (en quetzales) introducido en una mochila, respetando un límite de peso estricto y
dado que el espacio de búsqueda crece de forma exponencial (2^n combinaciones), el programa utiliza computación evolutiva para encontrar la solución óptima (o una muy cercana) evaluando solo una pequeña fracción de las posibilidades.

El motor genético simula el proceso de selección natural:
- Población Inicial: Genera soluciones candidatas (mochilas) con combinaciones de objetos al azar.
- Evaluación (Fitness): Calcula el valor de cada mochila y aplica una penalización matemática si la mochila excede la capacidad de peso máximo.
- Selección: Utiliza un sistema de "Torneo" para elegir a las mejores mochilas como padres.
- Cruza y Mutación: Combina el contenido de las mochilas seleccionadas y realiza alteraciones aleatorias para crear una nueva generación de soluciones.
- Elitismo: Protege a las mejores mochilas históricas para que no se pierdan en el proceso.
- teración: Repite el ciclo durante un número definido de generaciones hasta converger en una solución destacada.

Los parámetros modificables de este algoritmo son:
- Generaciones: El número de ciclos evolutivos, más generaciones dan más tiempo para encontrar la solución óptima, pero aumentan el tiempo de procesamiento.
- Población: La cantidad de individuos (mochilas) por generación, una población mayor explora más combinaciones simultáneamente, previniendo el estancamiento, pero consume más memoria.
- Mutación (0.0 - 1.0): La probabilidad de que un objeto se agregue o se quite de la mochila al azar (ejemplo 0.05 = 5%), es el motor de exploración para descubrir nuevas combinaciones, donde valores muy altos destruyen las buenas soluciones.
- Cruza (0.0 - 1.0): La probabilidad de que dos padres combinen sus inventarios para generar hijos (ejemplo 0.8 = 80%), es el motor de explotación para refinar buenas características.
- Torneo (Individuos): La cantidad de mochilas elegidas al azar para competir por ser padres, valores altos (ejemplo 10) crean una presión selectiva despiadada donde solo los mejores sobreviven, acelerando la convergencia pero arriesgando pérdida de diversidad genética.
- Elitismo (Individuos): La cantidad exacta de las mejores soluciones de la generación actual que pasarán intactas a la siguiente para garantizar que el puntaje máximo nunca retroceda.
- Penalización por kg: Los puntos restados al puntaje total (fitness) por cada kilogramo de sobrepeso, evita que el algoritmo haga "trampa" metiendo objetos valiosos pero pesados.

Por ejemplo, teniendo 24 objetos diferentes con los parámetros: Generaciones: 50 | Población: 20 | Mutación: 0.05 | Cruza: 0.8 | Torneo: 3 | Elitismo: 2 | Penalización: 800
<br>
Obtenemos el siguiente resultado donde se puede observar que el algoritmo no fue lo más preciso:
<br>
<img width="494" height="875" alt="image" src="https://github.com/user-attachments/assets/cec551d1-a127-4906-b0f1-b107676f1ed8" />
<br>
<br>
Por ejemplo, teniendo 24 objetos diferentes con los parámetros: Generaciones: 1000 | Población: 50 | Mutación: 0.05 | Cruza: 0.8 | Torneo: 3 | Elitismo: 2 | Penalización: 800
<br>
Obtenemos el siguiente resultado donde se puede observar que el algoritmo al tener muchas más generaciones y una mayor población obtuvo un resultado mucho más óptimo:
<br>
<img width="492" height="871" alt="image" src="https://github.com/user-attachments/assets/2344e154-be5c-46c5-ad41-536db8f57b97" />
<br>
<br>
Por ejemplo, teniendo 24 objetos diferentes con los parámetros: Generaciones: 1000 | Población: 50 | Mutación: 0.05 | Cruza: 0.8 | Torneo: 3 | Elitismo: 2 | Penalización: 20
<br>
Obtenemos el siguiente resultado donde se puede observar que dado que la penalización es muy pequeña (solo de 20 quetzales), el algoritmo tenderá mucho más a hacer trampa, ya que el castigo es muy pequeño, metiendo objetos muy pesados y de mucho valor:
<br>
<img width="494" height="878" alt="image" src="https://github.com/user-attachments/assets/e21359be-448d-408b-9c61-ff6b56eca9ea" />
<br>
<br>
Todas las librerías utilizadas para la realización de la tarea como numpy o matplotlib se encuentran en el archivo requirements.txt
