import tkinter as tk
from ui import MovieApp

def main():
    """Application entry point"""
    root = tk.Tk()
    app = MovieApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
