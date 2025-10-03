import tkinter as tk
from tkinter import messagebox

from Controllers.customer_controller import addCustomer
import greenButton
import redButton

# GUI setup
root = tk.Tk()
root.title("Add Customer")

tk.Label(root, text="Name").grid(row=0, column=0, padx=10, pady=5)
tk.Label(root, text="Email").grid(row=1, column=0, padx=10, pady=5)
tk.Label(root, text="Phone").grid(row=2, column=0, padx=10, pady=5)

entry_name = tk.Entry(root, width=30)
entry_email = tk.Entry(root, width=30)
entry_phone = tk.Entry(root, width=30)

entry_name.grid(row=0, column=1, padx=10, pady=5)
entry_email.grid(row=1, column=1, padx=10, pady=5)
entry_phone.grid(row=2, column=1, padx=10, pady=5)

def on_submit():
    name = entry_name.get().strip()
    email = entry_email.get().strip()
    phone = entry_phone.get().strip()
    if name and email:
        success, msg = addCustomer(name, email, phone)
        if success:
            messagebox.showinfo("Success", msg)
            greenButton.valid()
        else:
            messagebox.showerror("Error", msg)
            redButton.error()
    else:
        messagebox.showwarning("Missing Info", "Name and Email are required.")
        redButton.error()

tk.Button(root, text="Add Customer", command=on_submit).grid(row=3, column=0, columnspan=2, pady=10)
root.bing('<Return>',lambda event:on_submit())

root.mainloop()