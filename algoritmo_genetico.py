import random
import tkinter as tk
from tkinter import ttk
import threading
from dataclasses import dataclass
from typing import List, Callable


@dataclass(frozen=True)
class Item:
    name: str
    weight: float
    value: float

class KnapsackIndividual:
    def __init__(self, chromosome: List[int]):
        self.chromosome = tuple(chromosome)
        self._fitness = None

    def calculate_fitness(self, items: List[Item], max_weight: float, penalty: float) -> float:
        if self._fitness is not None:
            return self._fitness

        total_weight = sum(item.weight * gen for item, gen in zip(items, self.chromosome))
        total_value = sum(item.value * gen for item, gen in zip(items, self.chromosome))

        if total_weight > max_weight:
            self._fitness = max(0.0, total_value - (penalty * (total_weight - max_weight)))
        else:
            self._fitness = total_value

        return self._fitness

class GeneticAlgorithm:
    def __init__(self, population_size: int, mutation_rate: float, crossover_rate: float,
                 tournament_size: int, elitism_count: int,
                 fitness_function: Callable[[KnapsackIndividual], float]):
        self.pop_size = population_size
        self.mut_rate = mutation_rate
        self.cross_rate = crossover_rate
        self.tournament_size = tournament_size
        self.elitism_count = elitism_count
        self.fitness_function = fitness_function
        self.on_generation_done = None

    def _crossover(self, parent1: KnapsackIndividual, parent2: KnapsackIndividual) -> KnapsackIndividual:
        if random.random() > self.cross_rate:
            return KnapsackIndividual(list(parent1.chromosome))
        point = random.randint(1, len(parent1.chromosome) - 1)
        child_chromosome = list(parent1.chromosome[:point]) + list(parent2.chromosome[point:])
        return KnapsackIndividual(child_chromosome)

    def _mutate(self, individual: KnapsackIndividual) -> KnapsackIndividual:
        chromosome = list(individual.chromosome)
        for i in range(len(chromosome)):
            if random.random() < self.mut_rate:
                chromosome[i] = 1 - chromosome[i]
        return KnapsackIndividual(chromosome)

    def evolve(self, initial_population: List[KnapsackIndividual], generations: int) -> KnapsackIndividual:
        population = initial_population
        best_overall = None
        best_fitness = -1.0

        for gen in range(generations):
            pop_with_fitness = [(ind, self.fitness_function(ind)) for ind in population]
            pop_with_fitness.sort(key=lambda x: x[1], reverse=True)

            if pop_with_fitness[0][1] > best_fitness:
                best_overall = pop_with_fitness[0][0]
                best_fitness = pop_with_fitness[0][1]

            if self.on_generation_done:
                self.on_generation_done(gen + 1, generations, best_fitness)

            new_population = []

            elite_limit = min(self.elitism_count, len(pop_with_fitness))
            new_population.extend([ind for ind, fit in pop_with_fitness[:elite_limit]])

            while len(new_population) < self.pop_size:
                p1 = max(random.sample(pop_with_fitness, min(self.tournament_size, len(pop_with_fitness))),
                         key=lambda x: x[1])[0]
                p2 = max(random.sample(pop_with_fitness, min(self.tournament_size, len(pop_with_fitness))),
                         key=lambda x: x[1])[0]

                child = self._crossover(p1, p2)
                child = self._mutate(child)
                new_population.append(child)

            population = new_population

        return best_overall


class KnapsackApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Optimizador de Mochila - Algoritmo Genético")
        self.root.geometry("500x800")

        self.items = [
            Item("Laptop", 2.5, 500), Item("Cámara", 1.2, 300), Item("Termo", 0.8, 20),
            Item("Libro", 1.5, 40), Item("Chaqueta", 1.0, 60), Item("Botiquín", 0.6, 150),
            Item("Linterna", 0.4, 80), Item("Batería", 0.5, 90), Item("GPS", 0.3, 120),
            Item("Cuerda", 1.8, 45), Item("Tienda", 3.0, 200), Item("Comida", 2.0, 100),
            Item("Agua", 2.5, 80), Item("Brújula", 0.1, 30), Item("Cuchillo", 0.4, 75),
            Item("Fósforos", 0.05, 10), Item("Manta", 1.2, 50), Item("Saco dormir", 1.5, 110),
            Item("Prismáticos", 0.9, 140), Item("Gafas", 0.1, 40), Item("Repelente", 0.2, 25),
            Item("Radio", 0.6, 85), Item("Cargador Solar", 0.5, 130), Item("Botas", 1.4, 95),
        ]
        self.max_weight = 12.0

        self._build_ui()

    def _build_ui(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Inventario Disponible", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))

        inventory_text = " | ".join([f"{item.name} ({item.weight}kg, Q{item.value})" for item in self.items])
        inventory_box = tk.Text(frame, height=3, wrap=tk.WORD, state=tk.NORMAL)
        inventory_box.insert(tk.END, inventory_text)
        inventory_box.config(state=tk.DISABLED)
        inventory_box.pack(fill=tk.X, pady=(0, 15))

        # Contenedor de parámetros ampliado
        params_frame = ttk.LabelFrame(frame, text="Parámetros del Algoritmo", padding="10")
        params_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(params_frame, text="Generaciones:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entry_gen = ttk.Entry(params_frame, width=10)
        self.entry_gen.insert(0, "50")
        self.entry_gen.grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)

        ttk.Label(params_frame, text="Población:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entry_pop = ttk.Entry(params_frame, width=10)
        self.entry_pop.insert(0, "20")
        self.entry_pop.grid(row=1, column=1, sticky=tk.W, pady=2, padx=5)

        ttk.Label(params_frame, text="Mutación (0.0-1.0):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entry_mut = ttk.Entry(params_frame, width=10)
        self.entry_mut.insert(0, "0.05")
        self.entry_mut.grid(row=2, column=1, sticky=tk.W, pady=2, padx=5)

        ttk.Label(params_frame, text="Cruza (0.0-1.0):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.entry_cross = ttk.Entry(params_frame, width=10)
        self.entry_cross.insert(0, "0.8")
        self.entry_cross.grid(row=3, column=1, sticky=tk.W, pady=2, padx=5)

        ttk.Label(params_frame, text="Torneo (Individuos):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.entry_tour = ttk.Entry(params_frame, width=10)
        self.entry_tour.insert(0, "3")
        self.entry_tour.grid(row=4, column=1, sticky=tk.W, pady=2, padx=5)

        ttk.Label(params_frame, text="Elitismo (Individuos):").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.entry_elite = ttk.Entry(params_frame, width=10)
        self.entry_elite.insert(0, "2")
        self.entry_elite.grid(row=5, column=1, sticky=tk.W, pady=2, padx=5)

        ttk.Label(params_frame, text="Penalización por kg:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.entry_pen = ttk.Entry(params_frame, width=10)
        self.entry_pen.insert(0, "800.0")
        self.entry_pen.grid(row=6, column=1, sticky=tk.W, pady=2, padx=5)

        self.run_btn = ttk.Button(frame, text="Ejecutar Algoritmo Genético", command=self.start_algorithm_thread)
        self.run_btn.pack(pady=(0, 10))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))

        self.status_label = ttk.Label(frame, text="Listo.")
        self.status_label.pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(frame, text="Mejor Solución Encontrada", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.result_text = tk.Text(frame, height=12, state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True)

    def start_algorithm_thread(self):
        try:
            gen = int(self.entry_gen.get())
            pop = int(self.entry_pop.get())
            mut = float(self.entry_mut.get())
            cross = float(self.entry_cross.get())
            tour = int(self.entry_tour.get())
            elite = int(self.entry_elite.get())
            pen = float(self.entry_pen.get())
        except ValueError:
            self._display_result("Error: Verifica que los números y decimales sean válidos.")
            return

        self.run_btn.config(state=tk.DISABLED)
        self._display_result("Calculando...")
        self.progress_var.set(0)

        thread = threading.Thread(
            target=self._run_algorithm_logic,
            args=(gen, pop, mut, cross, tour, elite, pen),
            daemon=True
        )
        thread.start()

    def _run_algorithm_logic(self, gen, pop, mut, cross, tour, elite, pen):
        def knapsack_fitness(individual: KnapsackIndividual) -> float:
            return individual.calculate_fitness(self.items, self.max_weight, pen)

        chromosome_length = len(self.items)
        initial_pop = [
            KnapsackIndividual([random.choice([0, 1]) for _ in range(chromosome_length)])
            for _ in range(pop)
        ]

        ga = GeneticAlgorithm(
            population_size=pop,
            mutation_rate=mut,
            crossover_rate=cross,
            tournament_size=tour,
            elitism_count=elite,
            fitness_function=knapsack_fitness
        )

        ga.on_generation_done = self._update_progress

        best_solution = ga.evolve(initial_pop, gen)

        self.root.after(0, self._format_and_display_results, best_solution)
        self.root.after(0, lambda: self.run_btn.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.status_label.config(text="Evolución completada"))

    def _update_progress(self, current_gen: int, total_gens: int, best_fitness: float):
        progress_percent = (current_gen / total_gens) * 100
        self.root.after(0, self.progress_var.set, progress_percent)

        status_text = f"Generación: {current_gen}/{total_gens} | Mejor Fitness actual: ${best_fitness:.2f}"
        self.root.after(0, lambda: self.status_label.config(text=status_text))

    def _format_and_display_results(self, best_solution: KnapsackIndividual):
        total_w, total_v = 0.0, 0.0
        result_lines = []

        for i, gen in enumerate(best_solution.chromosome):
            if gen == 1:
                item = self.items[i]
                result_lines.append(f"{item.name} (Peso: {item.weight}kg, Valor: ${item.value})")
                total_w += item.weight
                total_v += item.value

        result_lines.append("-" * 30)
        result_lines.append(f"Peso Total:  {total_w:.2f} kg / {self.max_weight} kg")
        result_lines.append(f"Valor Total: Q{total_v:.2f}")

        if total_w > self.max_weight:
            result_lines.append("\nLa mochila superó el peso máximo (penalizada)")

        self._display_result("\n".join(result_lines))

    def _display_result(self, message: str):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, message)
        self.result_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = KnapsackApp(root)
    root.mainloop()