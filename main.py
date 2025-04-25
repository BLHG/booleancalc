import ast
import tkinter as tk
import re
import itertools


class Root(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Boolean Calculator")
        self.shared_result = tk.StringVar()
        self.geometry("420x500")
        self.minsize(420, 500)
        self.configure(background="black")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container = tk.Frame(self, bg='white')

        container.grid(row=0, column=0, sticky='news')
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (CalcScreen, ResultScreen):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(CalcScreen)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        if cont == ResultScreen:
            frame.update_result()


class CalcScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg='black')
        self.rowconfigure(0, weight=2)
        self.columnconfigure(0, weight=1)
        self.btn_id = -1
        self.result = 0

        cnt = tk.Label(self,
               text='Введите логическое выражение' if not expression else f'{" ".join(expression)}',
               font=('Arial', 20),
               borderwidth=10,
               bg='#1c1c1c',
               fg='white',
               highlightbackground="white",
               highlightthickness=1)
        cnt.grid(row=0, column=0, stick='nsew', columnspan=3)

        for r in range(3):
            self.rowconfigure(r+1, weight=1)
            for c in range(3):
                self.columnconfigure(c, weight=1)
                self.btn_id += 1
                buttons.append(tk.Button(self,
                                         text=commands[self.btn_id],
                                         font=('Arial', 20)))
                if self.btn_id < 8:
                    buttons[int(self.btn_id)].config(
                        bg='#1c1c1c',
                        fg='white',
                        command=lambda tc=self.btn_id: numb_append(tc))
                    buttons[int(self.btn_id)].bind("<Enter>", on_enter1)
                    buttons[int(self.btn_id)].bind("<Leave>", on_leave1)
                else:
                    buttons[int(self.btn_id)].config(
                        bg='#f5a742',
                        fg='white',
                        command=lambda: numb_comp(expression))
                    buttons[int(self.btn_id)].bind("<Enter>", on_enter2)
                    buttons[int(self.btn_id)].bind("<Leave>", on_leave2)
                buttons[int(self.btn_id)].grid(row=r+1, column=c, sticky="news")

        def numb_append(btn_nr):
            expression.append(commands[btn_nr])
            new_text = (
                f'{" ".join(expression)}'
                if expression
                else 'Введите логическое выражение')
            cnt.config(text=new_text)

        def numb_comp(inp):
            answer = ' '.join(inp)
            final.append(answer)
            new_text = (
                f'{" ".join(expression)}'
                if expression
                else 'Введите логическое выражение')
            cnt.config(text=new_text)
            try:
                result_value = Results(variables, final)
                self.controller.shared_result.set(str(result_value))
                controller.show_frame(ResultScreen)
            except InvalidEquation:
                cnt.config(text="Некорректное выражение")
            expression.clear()
            variables.clear()
            final.clear()


        def key_press(event):
            if event.keycode in range(65, 91):
                expression.append(event.char.upper())
                new_text = (
                    f'{" ".join(expression)}'
                    if expression
                    else 'Введите логическое выражение')
                cnt.config(text=new_text)
                if event.char.upper() not in variables:
                    variables.append(event.char.upper())
            elif event.keycode == 8:
                try:
                    tl = []
                    del expression[-1]
                    for aa in variables:
                        if aa in expression:
                            tl.append(aa)
                    variables.clear()
                    variables.extend(tl)
                except IndexError:
                    pass
                new_text = (
                    f'{" ".join(expression)}'
                    if expression
                    else 'Введите логическое выражение')
                cnt.config(text=new_text)

        self.bind_all('<KeyPress>', key_press)


class ResultScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg='#1c1c1c')
        self.result = self.controller.shared_result.get()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, bg='#1c1c1c')
        self.scrollbar1 = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar2 = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#1c1c1c')

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar1.set, xscrollcommand=self.scrollbar2.set)

        self.rtrn = tk.Button(
            self.scrollable_frame,
            text='Назад',
            command=lambda: controller.show_frame(CalcScreen),
            bg='#f5a742',
            fg='white',
            font=('Arial', 14)
        )
        self.rtrn.grid(row=0, column=0, pady=10, sticky="nw")

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar1.grid(row=0, column=1, sticky="ns")
        self.scrollbar2.grid(row=1, column=0, sticky="ew")

        self.scrollable_frame.grid_rowconfigure(0, weight=0)
        self.scrollable_frame.grid_rowconfigure(1, weight=1)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

    def update_result(self):
        global labels
        labels.clear()
        for widget in self.scrollable_frame.winfo_children():
            if widget != self.rtrn:
                widget.destroy()

        self.lbl_id = -1
        result_str = self.controller.shared_result.get()
        parsed_data = ast.literal_eval(result_str)
        self.result_tuple = tuple(parsed_data)
        for r in range(len(self.result_tuple)):
            for c in range(len(self.result_tuple[0])):
                self.lbl_id += 1
                labels.append(tk.Label(
                    self.scrollable_frame,
                    text=self.result_tuple[r][c],
                    font=('Arial', 20),
                    bg='#1c1c1c',
                    fg='white',
                    height=2,
                    width=10,
                    highlightbackground="white",
                    highlightthickness=1
                ))
                if c == len(self.result_tuple[0])-1:
                    labels[int(self.lbl_id)].config(width=len(self.result_tuple[0][c].split())*3)
                labels[int(self.lbl_id)].grid(row=r+1, column=c)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.update_idletasks()





class Vessel(object):
    pass

class Results(object):
    def __init__(self, base=None, phrases=None):
          self.base = base
          self.phrases = phrases or []
          self.base_conditions = list(itertools.product([False, True], repeat=len(base)))
          self.p = re.compile('(?<!\\w)(' + '|'.join(self.base) + ')(?!\\w)')
          self.replacements = [(r'∧', 'and'),
                    (r'∨', 'or'),
                    (r'¬', 'not'),
                    (r'→', r'<='),
                    (r'⊕', r'^'),
                    (r'↔', r'=='),
                    (r'True', r'1'),
                    (r'False', r'0')]
    def translate(self):
        for ind in range(len(self.phrases)):
            for pattern, repl in self.replacements:
                while re.search(pattern, self.phrases[ind]) != None:
                    self.phrases[ind] = re.sub(pattern, repl, self.phrases[ind])
        return self.phrases

    def calculate(self, *args):
        v = Vessel()
        for a, b in zip(self.base, args):
            setattr(v, a, b)

        eval_phrases = []
        for item in self.translate():
            item = self.p.sub(r'v.\1', item)
            try:
                eval_phrases.append(eval(item))
            except Exception:
                raise InvalidEquation('Whoops! You entered a bad string :3')

        row = [getattr(v, b) for b in self.base] + eval_phrases
        return [int(item) for item in row]


    def __str__(self):
        rt = list()
        r = list()
        for i in range(len(self.base)):
            rt.append(self.base[i])
        rt.append(' '.join(expression))
        r.append(rt)
        for conditions in self.base_conditions:
            r.append(self.calculate(*conditions))
        return str(r)

class InvalidEquation(Exception):
    def __init__(self, message):
        super().__init__(message)
        pass



def on_enter1(e):
    e.widget.config(bg='#2e2e2e')

def on_enter2(e):
    e.widget.config(bg='#ffb759')

def on_leave1(e):
    e.widget.config(bg='#1c1c1c')

def on_leave2(e):
    e.widget.config(bg='#ffb14d')

expression = []
commands = ('∧', '∨', '¬', '→', '↔', '⊕' , '(', ')', '=')
repls = [(r'∧', 'and'),
        (r'∨', 'or'),
        (r'¬', 'not'),
        (r'(\S+)\s*→\s*(\S+)', r'not \1 or \2'),
        (r'↔', r'^'),
        (r'⊕', r'!='),
        (r'True', r'1'),
        (r'False', r'0')]

buttons = []
labels = []
variables = []
final = []


if __name__ == '__main__':
    app = Root()
    app.mainloop()

