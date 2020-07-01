import tkinter as tk
import random
import copy
import os
import time
from functools import partial
from operator import itemgetter


class Logging(tk.Frame):
    def __init__(self, master=None, data=None):
        tk.Frame.__init__(self, master)
        self.root = tk.Widget._nametowidget(self, master.winfo_parent())
        self.text = tk.StringVar()
        self.generation = tk.StringVar()
        self.generation_num = 0
        self.generation.set("Generation {}".format(self.generation_num + 1))
        self.data = data
        self.__init()

    def __init(self):
        self.__generation = tk.Label(self, textvariable=self.generation)
        self.__target = tk.Label(
            self, textvariable=self.text, font=('times', 17))
        self.__pack()
        SimpleGA(self, self.data)

    def __pack(self):
        self.__generation.pack(fill='both')
        self.__target.pack(fill='both')
        self.pack(padx=50, pady=(50, 0))

    def simple(self, data):
        self.generation_num += 1
        self.generation.set("Generation {}".format(self.generation_num))
        self.text.set(data)
        self.update()


class SimpleGA:
    def __init__(self, master=None, data=None):
        self.data = data
        self.log_window = master
        self.__init()

    def __init(self):
        self.loop = True
        self.populations = self.__population(
            self.data['population'], self.data['target'])
        while self.loop:
            self.parent = self.__selections(self.populations)
            self.childs = self.__crossover(self.parent)
            self.mutation = self.__mutations(self.childs)
            self.populations = self.__regenerations(
                self.populations, self.mutation.copy())
            self.solution = self.__solution(self.populations)
            self.log_window.simple(self.solution['genetic'])
            time.sleep(0.01)
            if self.solution['genetic'] == self.data['target']:
                self.loop = False

    def __genetic(self, target):
        genetic = ''
        for i in range(len(target)):
            genetic += chr(random.randint(32, 126))
        return genetic

    def __fitness(self, genetic, target):
        return (sum([a == list(genetic)[i] for i, a in enumerate(list(target))]) / len(target)) * 100

    def __population(self, size, target):
        populations = []
        for x in range(size):
            genetic = self.__genetic(target)
            population = {'genetic': genetic,
                          'fitness': self.__fitness(genetic, target)}
            populations.append(population)
        return populations

    def __selections(self, populations):
        return sorted(populations, reverse=True, key=itemgetter('fitness'))[
            :len(populations)//2]

    def __crossover(self, parents):
        crossover, childs = [], ''
        cp = len(self.data['target']) // 2
        parent = copy.deepcopy(parents)
        for i, x in enumerate(parent):
            if i > 0:
                childs += parent[i-1]['genetic'][:cp]
                childs += x['genetic'][cp:]
                x['genetic'] = childs
                crossover.append(x)
                childs = ''
            else:
                childs += parent[-1]['genetic'][:cp]
                childs += x['genetic'][cp:]
                x['genetic'] = childs
                crossover.append(x)
                childs = ''
        return crossover

    def __mutations(self, childs):
        mutations, mutants = [], ''
        target = self.data['target']
        children = copy.deepcopy(childs)
        for x in children:
            for i, y in enumerate(x['genetic']):
                if random.random() <= self.data['mutation']:
                    if y == target[i]:
                        mutants += y
                    else:
                        mutants += chr(random.randint(32, 126))
                else:
                    mutants += y
            x['genetic'] = mutants
            x['fitness'] = self.__fitness(mutants, target)
            mutants = ''
            mutations.append(x)
        return mutations

    def __regenerations(self, populations, children):
        population = sorted(populations, reverse=True, key=itemgetter('fitness'))[
            :len(populations)//2] + children
        return population

    def __solution(self, population):
        best = max(range(len(population)),
                   key=lambda index: population[index]['fitness'])
        return population[best]


class MainMenu(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.__form_frame = tk.Frame(self)
        self.data = {
            'target': tk.StringVar(value="I'ts Just String"),
            'population': tk.IntVar(value=10),
            'mutation': tk.DoubleVar(value=0.5),
            'is_delay': tk.BooleanVar(value=False),
            'delay': tk.DoubleVar(value=0.001),
            'log_type': tk.StringVar(None, 'simple')
        }
        self.__init()

    def __init(self):
        self.__title = tk.Label(
            self, text="Simple Genetic Algorithm", font=("times", 20))
        self.__form()
        self.__pack()

    def __form(self):
        self.__target_label = tk.Label(self.__form_frame, text='Target')
        self.__target_entry = tk.Entry(
            self.__form_frame, textvariable=self.data['target'])
        self.__population_size_label = tk.Label(
            self.__form_frame, text="Population Size")
        self.__population_size_entry = tk.Entry(
            self.__form_frame, textvariable=self.data['population'])
        self.__mutation_rate_label = tk.Label(
            self.__form_frame, text="Mutation Rate")
        self.__mutation_rate_entry = tk.Entry(
            self.__form_frame, textvariable=self.data['mutation'])
        self.__start_button = tk.Button(
            self.__form_frame, text="Start", command=self.start, width=8)
        self.delay_toogle = tk.Checkbutton(
            self.__form_frame, text="Delay", variable=self.data['is_delay'], command=self.delay_toggler)
        self.__delay_label = tk.Label(self.__form_frame, text="Delay (sec)")
        self.__delay_entry = tk.Entry(
            self.__form_frame, textvariable=self.data['delay'])
        self.__is_simple = tk.Radiobutton(
            self.__form_frame, variable=self.data['log_type'], value='simple', text='Simple')
        self.__is_verbose = tk.Radiobutton(
            self.__form_frame, variable=self.data['log_type'], value='verbose', text='Verbose')
        self.__is_verbose.deselect()

    def __pack(self):
        self.__title.pack(side='top', anchor='nw')
        self.__target_label.grid(row=0, column=0, sticky='w', padx=(3, 5))
        self.__target_entry.grid(row=0, column=1)
        self.__population_size_label.grid(
            row=1, column=0, sticky='w', padx=(3, 5))
        self.__population_size_entry.grid(row=1, column=1)
        self.__mutation_rate_label.grid(
            row=2, column=0, sticky='w', padx=(3, 5))
        self.__mutation_rate_entry.grid(row=2, column=1)
        self.__start_button.grid(
            row=0, column=3, rowspan=3, sticky='nswe', padx=5)
        self.delay_toogle.grid(row=3, column=3, sticky='w')
        self.__is_simple.grid(row=4, column=0)
        self.__is_verbose.grid(row=4, column=1)
        self.__form_frame.pack(side='top', anchor='w')
        self.pack()

    def get_data(self):
        return {
            'target': str(self.__target_entry.get()),
            'population': int(self.__population_size_entry.get()),
            'mutation': float(self.__mutation_rate_entry.get()),
        }

    def start(self):
        main = tk.Widget._nametowidget(self, self.winfo_parent())
        root = tk.Widget._nametowidget(self, self.master.winfo_parent())
        root.geometry("600x600")
        main.start(self.get_data())

    def delay_toggler(self):
        toggle = self.data['is_delay'].get()
        if toggle:
            self.__delay_label.grid(row=3, column=0, sticky='w')
            self.__delay_entry.grid(row=3, column=1)
        else:
            self.__delay_label.grid_forget()
            self.__delay_entry.grid_forget()


class MainWindow(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.__init()

    def __init(self):
        self.__main_menu = MainMenu(self)
        self.__pack()

    def __pack(self):
        self.__main_menu.pack(anchor='center')
        self.pack()

    def start(self, data):
        self.__logging = Logging(self, data)
        self.__logging.pack()


def main():
    root = tk.Tk()
    root.title("Simple Genetic Algorithm")
    root.resizable(0, 0)
    window = MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()

# lanjut logging verbose dan buggy buggy asshole
