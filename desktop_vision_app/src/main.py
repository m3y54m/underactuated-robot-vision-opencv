import tkinter as tk

class RobotVisionUI():
    def __init__(self):
        self.root = tk.Tk()

        self.label = tk.Label(self.root, text="Blank")
        self.label.pack()

        self.button = tk.Button(self.root, text="Say Hello!", command=self.update_label)
        self.button.pack()

        self.root.mainloop()

    def update_label(self):
        self.label.configure(text="Hello World!")

if __name__ == "__main__":
    ui = RobotVisionUI()
