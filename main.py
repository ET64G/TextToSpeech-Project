from tkinter import Tk
from gui import PdfTtsApp

def main() -> None:
    root = Tk()
    app = PdfTtsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    

