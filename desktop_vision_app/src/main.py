import tkinter as tk


def update_label():
    label.configure(text="Hello World!")


root = tk.Tk()

label = tk.Label(root, text="Blank")
label.pack()

button = tk.Button(root, text="Say Hello!", command=update_label)
button.pack()

root.mainloop()
