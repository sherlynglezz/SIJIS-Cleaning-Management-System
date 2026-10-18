"""Tkinter application for SIJI'S Luxe & Sparkle."""

import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from models import Appointment, CleaningService, Customer


DATA_FILE = Path(__file__).with_name("sijis_data.json")

# Tuple of fixed starting services. Add-ons are stored in a dictionary.
DEFAULT_SERVICES = (
    ("Standard Cleaning", 150.00),
    ("Bi-Weekly Cleaning", 180.00),
    ("Deep Cleaning", 250.00),
    ("Move-In/Move-Out Cleaning", 300.00),
)

DEFAULT_ADD_ONS = {
    "Oven Interior": 25.00,
    "Refrigerator Interior": 25.00,
    "Baseboards": 20.00,
    "Inside Cabinets": 30.00,
    "Organization (1 hour)": 40.00,
}


class CleaningManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SIJI'S Luxe & Sparkle Cleaning Management System")
        self.root.geometry("950x650")
        self.root.minsize(850, 580)

        self.customers = []
        self.services = [
            CleaningService(name, price, DEFAULT_ADD_ONS.copy())
            for name, price in DEFAULT_SERVICES
        ]
        self.appointments = []
        self.add_on_vars = {}

        self.configure_style()
        self.build_interface()
        self.load_data()
        self.refresh_all_views()

    def configure_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Heading.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("TButton", padding=7)

    def build_interface(self):
        header = ttk.Frame(self.root, padding=(18, 15))
        header.pack(fill="x")
        ttk.Label(header, text="SIJI'S Luxe & Sparkle", style="Title.TLabel").pack(
            side="left"
        )
        ttk.Label(header, text="Cleaning Management System").pack(
            side="left", padx=15
        )

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.customer_tab = ttk.Frame(self.notebook, padding=15)
        self.service_tab = ttk.Frame(self.notebook, padding=15)
        self.appointment_tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.customer_tab, text="Customers")
        self.notebook.add(self.service_tab, text="Services & Prices")
        self.notebook.add(self.appointment_tab, text="Appointments")
        self.build_customer_tab()
        self.build_service_tab()
        self.build_appointment_tab()

    def build_customer_tab(self):
        form = ttk.LabelFrame(self.customer_tab, text="Add Customer", padding=12)
        form.pack(fill="x")
        self.customer_name = tk.StringVar()
        self.customer_phone = tk.StringVar()
        self.customer_address = tk.StringVar()
        fields = (
            ("Name", self.customer_name),
            ("Phone", self.customer_phone),
            ("Address", self.customer_address),
        )
        for row, (label, variable) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=4)
            ttk.Entry(form, textvariable=variable, width=50).grid(
                row=row, column=1, sticky="ew", padx=10, pady=4
            )
        form.columnconfigure(1, weight=1)
        ttk.Button(form, text="Add Customer", command=self.add_customer).grid(
            row=3, column=1, sticky="e", pady=(10, 0)
        )

        table_frame = ttk.LabelFrame(self.customer_tab, text="Customers", padding=10)
        table_frame.pack(fill="both", expand=True, pady=(15, 0))
        self.customer_tree = ttk.Treeview(
            table_frame,
            columns=("id", "name", "phone", "address"),
            show="headings",
        )
        for column, heading, width in (
            ("id", "ID", 55),
            ("name", "Name", 180),
            ("phone", "Phone", 140),
            ("address", "Address", 350),
        ):
            self.customer_tree.heading(column, text=heading)
            self.customer_tree.column(column, width=width, anchor="w")
        self.customer_tree.pack(fill="both", expand=True)

    def build_service_tab(self):
        ttk.Label(
            self.service_tab,
            text="Available Cleaning Services",
            style="Heading.TLabel",
        ).pack(anchor="w", pady=(0, 10))
        self.service_tree = ttk.Treeview(
            self.service_tab,
            columns=("service", "price"),
            show="headings",
            height=8,
        )
        self.service_tree.heading("service", text="Service")
        self.service_tree.heading("price", text="Base Price")
        self.service_tree.column("service", width=400)
        self.service_tree.column("price", width=160)
        self.service_tree.pack(fill="x")

        add_on_frame = ttk.LabelFrame(
            self.service_tab, text="Available Add-On Services", padding=12
        )
        add_on_frame.pack(fill="x", pady=(18, 0))
        for row, (name, price) in enumerate(DEFAULT_ADD_ONS.items()):
            ttk.Label(add_on_frame, text=name).grid(row=row, column=0, sticky="w")
            ttk.Label(add_on_frame, text=f"${price:,.2f}").grid(
                row=row, column=1, sticky="e", padx=20, pady=4
            )

    def build_appointment_tab(self):
        form = ttk.LabelFrame(
            self.appointment_tab, text="Schedule Appointment", padding=12
        )
        form.pack(fill="x")
        self.appointment_customer = tk.StringVar()
        self.appointment_service = tk.StringVar()
        self.appointment_date = tk.StringVar()
        self.appointment_time = tk.StringVar()

        ttk.Label(form, text="Customer").grid(row=0, column=0, sticky="w", pady=4)
        self.customer_combo = ttk.Combobox(
            form, textvariable=self.appointment_customer, state="readonly", width=35
        )
        self.customer_combo.grid(row=0, column=1, sticky="ew", padx=10, pady=4)
        ttk.Label(form, text="Service").grid(row=1, column=0, sticky="w", pady=4)
        self.service_combo = ttk.Combobox(
            form, textvariable=self.appointment_service, state="readonly", width=35
        )
        self.service_combo.grid(row=1, column=1, sticky="ew", padx=10, pady=4)
        self.service_combo.bind("<<ComboboxSelected>>", self.update_estimate)
        ttk.Label(form, text="Date (YYYY-MM-DD)").grid(
            row=2, column=0, sticky="w", pady=4
        )
        ttk.Entry(form, textvariable=self.appointment_date).grid(
            row=2, column=1, sticky="ew", padx=10, pady=4
        )
        ttk.Label(form, text="Time (example: 10:30 AM)").grid(
            row=3, column=0, sticky="w", pady=4
        )
        ttk.Entry(form, textvariable=self.appointment_time).grid(
            row=3, column=1, sticky="ew", padx=10, pady=4
        )

        add_on_frame = ttk.Frame(form)
        add_on_frame.grid(row=0, column=2, rowspan=4, sticky="nsew", padx=(20, 0))
        ttk.Label(add_on_frame, text="Add-Ons", style="Heading.TLabel").pack(
            anchor="w"
        )
        for name in DEFAULT_ADD_ONS:
            variable = tk.BooleanVar()
            variable.trace_add("write", self.update_estimate)
            self.add_on_vars[name] = variable
            ttk.Checkbutton(add_on_frame, text=name, variable=variable).pack(anchor="w")

        form.columnconfigure(1, weight=1)
        self.estimate_label = ttk.Label(form, text="Estimated Total: $0.00")
        self.estimate_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=12)
        ttk.Button(
            form, text="Schedule Appointment", command=self.schedule_appointment
        ).grid(row=4, column=2, sticky="e", pady=8)

        table_frame = ttk.LabelFrame(
            self.appointment_tab, text="Scheduled Appointments", padding=10
        )
        table_frame.pack(fill="both", expand=True, pady=(15, 0))
        self.appointment_tree = ttk.Treeview(
            table_frame,
            columns=("id", "customer", "service", "date", "time", "total", "status"),
            show="headings",
        )
        for column, heading, width in (
            ("id", "ID", 45),
            ("customer", "Customer", 140),
            ("service", "Service", 180),
            ("date", "Date", 95),
            ("time", "Time", 90),
            ("total", "Total", 85),
            ("status", "Status", 85),
        ):
            self.appointment_tree.heading(column, text=heading)
            self.appointment_tree.column(column, width=width, anchor="w")
        self.appointment_tree.pack(fill="both", expand=True)
        ttk.Button(
            table_frame, text="Cancel Selected", command=self.cancel_selected
        ).pack(anchor="e", pady=(8, 0))

    def add_customer(self):
        name = self.customer_name.get().strip()
        phone = self.customer_phone.get().strip()
        address = self.customer_address.get().strip()
        if not name or not phone or not address:
            messagebox.showerror("Missing Information", "Please complete every field.")
            return
        next_id = max((customer.customer_id for customer in self.customers), default=0) + 1
        self.customers.append(Customer(next_id, name, phone, address))
        self.customer_name.set("")
        self.customer_phone.set("")
        self.customer_address.set("")
        self.save_data()
        self.refresh_all_views()
        messagebox.showinfo("Customer Added", f"{name} was added successfully.")

    def selected_add_ons(self):
        return [name for name, variable in self.add_on_vars.items() if variable.get()]

    def update_estimate(self, *_args):
        service = self.find_service(self.appointment_service.get())
        total = service.calculate_price(self.selected_add_ons()) if service else 0
        self.estimate_label.config(text=f"Estimated Total: ${total:,.2f}")

    def schedule_appointment(self):
        customer = self.find_customer(self.appointment_customer.get())
        service = self.find_service(self.appointment_service.get())
        date = self.appointment_date.get().strip()
        time = self.appointment_time.get().strip().upper()
        if not customer or not service or not date or not time:
            messagebox.showerror(
                "Missing Information", "Please select a customer and complete every field."
            )
            return
        next_id = max(
            (appointment.appointment_id for appointment in self.appointments), default=0
        ) + 1
        appointment = Appointment(
            next_id, customer, service, date, time, self.selected_add_ons()
        )
        try:
            appointment.validate_schedule()
        except ValueError:
            messagebox.showerror(
                "Invalid Date or Time",
                "Use YYYY-MM-DD for the date and a time such as 10:30 AM.",
            )
            return
        self.appointments.append(appointment)
        self.appointment_date.set("")
        self.appointment_time.set("")
        for variable in self.add_on_vars.values():
            variable.set(False)
        self.save_data()
        self.refresh_appointments()
        self.update_estimate()
        messagebox.showinfo("Appointment Scheduled", "The appointment was saved.")

    def cancel_selected(self):
        selected = self.appointment_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select an appointment to cancel.")
            return
        appointment_id = int(self.appointment_tree.item(selected[0], "values")[0])
        for appointment in self.appointments:
            if appointment.appointment_id == appointment_id:
                appointment.cancel_appointment()
                break
        self.save_data()
        self.refresh_appointments()

    def find_customer(self, display_value):
        if not display_value:
            return None
        customer_id = int(display_value.split(" - ", 1)[0])
        return next(
            (customer for customer in self.customers if customer.customer_id == customer_id),
            None,
        )

    def find_service(self, service_name):
        return next(
            (service for service in self.services if service.service_name == service_name),
            None,
        )

    def refresh_all_views(self):
        self.refresh_customers()
        self.refresh_services()
        self.refresh_appointments()

    def refresh_customers(self):
        for row in self.customer_tree.get_children():
            self.customer_tree.delete(row)
        for customer in self.customers:
            self.customer_tree.insert(
                "", "end", values=(customer.customer_id, customer.name, customer.phone, customer.address)
            )
        self.customer_combo["values"] = [
            f"{customer.customer_id} - {customer.name}" for customer in self.customers
        ]

    def refresh_services(self):
        for row in self.service_tree.get_children():
            self.service_tree.delete(row)
        for service in self.services:
            self.service_tree.insert(
                "", "end", values=(service.service_name, f"${service.base_price:,.2f}")
            )
        self.service_combo["values"] = [service.service_name for service in self.services]

    def refresh_appointments(self):
        for row in self.appointment_tree.get_children():
            self.appointment_tree.delete(row)
        for appointment in self.appointments:
            self.appointment_tree.insert(
                "",
                "end",
                values=(
                    appointment.appointment_id,
                    appointment.customer.name,
                    appointment.service.service_name,
                    appointment.date,
                    appointment.time,
                    f"${appointment.calculate_total():,.2f}",
                    appointment.status,
                ),
            )

    def save_data(self):
        data = {
            "customers": [customer.to_dict() for customer in self.customers],
            "appointments": [appointment.to_dict() for appointment in self.appointments],
        }
        DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load_data(self):
        if not DATA_FILE.exists():
            return
        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            self.customers = [Customer.from_dict(item) for item in data.get("customers", [])]
            customers = {customer.customer_id: customer for customer in self.customers}
            services = {service.service_name: service for service in self.services}
            for item in data.get("appointments", []):
                customer = customers.get(int(item["customer_id"]))
                service = services.get(item["service_name"])
                if customer and service:
                    self.appointments.append(
                        Appointment(
                            int(item["appointment_id"]),
                            customer,
                            service,
                            item["date"],
                            item["time"],
                            item.get("selected_add_ons", []),
                            item.get("status", "Scheduled"),
                        )
                    )
        except (OSError, ValueError, KeyError, TypeError):
            messagebox.showwarning(
                "Data Warning",
                "Saved data could not be loaded. The program will start with empty records.",
            )


def main():
    root = tk.Tk()
    CleaningManagementApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
