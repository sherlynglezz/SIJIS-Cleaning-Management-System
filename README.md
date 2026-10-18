# SIJI'S Luxe & Sparkle Cleaning Management System

A Python desktop application for managing customers, cleaning services,
estimated prices, and appointments for SIJI'S Luxe & Sparkle.

## Project Features

- Add and view customer information.
- View cleaning services and prices.
- Select optional add-on services.
- Calculate an estimated appointment total.
- Schedule, view, and cancel appointments.
- Save customers and appointments between sessions.

## Required Python Classes

- `Customer`
- `CleaningService`
- `Appointment`

The Tkinter interface interacts with all three classes. The program also uses
lists, a tuple, and dictionaries to organize its data.

## Run the Program

Open the project folder in VS Code and run:

```bash
python app.py
```

## Run the Tests

```bash
python -m unittest test_models.py
```

The application uses only modules included with Python.
