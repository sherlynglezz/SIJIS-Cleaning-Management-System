"""Core classes for the SIJI'S cleaning management system."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Customer:
    customer_id: int
    name: str
    phone: str
    address: str

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "phone": self.phone,
            "address": self.address,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(int(data["customer_id"]), data["name"], data["phone"], data["address"])


@dataclass
class CleaningService:
    service_name: str
    base_price: float
    add_ons: dict = field(default_factory=dict)

    def calculate_price(self, selected_add_ons=None):
        selected_add_ons = selected_add_ons or []
        return self.base_price + sum(
            self.add_ons[name] for name in selected_add_ons if name in self.add_ons
        )

    def to_dict(self):
        return {
            "service_name": self.service_name,
            "base_price": self.base_price,
            "add_ons": self.add_ons,
        }


@dataclass
class Appointment:
    appointment_id: int
    customer: Customer
    service: CleaningService
    date: str
    time: str
    selected_add_ons: list = field(default_factory=list)
    status: str = "Scheduled"

    def calculate_total(self):
        return self.service.calculate_price(self.selected_add_ons)

    def cancel_appointment(self):
        self.status = "Canceled"

    def validate_schedule(self):
        datetime.strptime(f"{self.date} {self.time}", "%Y-%m-%d %I:%M %p")
        return True

    def to_dict(self):
        return {
            "appointment_id": self.appointment_id,
            "customer_id": self.customer.customer_id,
            "service_name": self.service.service_name,
            "date": self.date,
            "time": self.time,
            "selected_add_ons": self.selected_add_ons,
            "status": self.status,
        }
