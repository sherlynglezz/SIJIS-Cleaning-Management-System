"""Unit tests for the three core project classes."""

import unittest

from models import Appointment, CleaningService, Customer


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.customer = Customer(1, "Maria Lopez", "812-555-0101", "100 Main St")
        self.service = CleaningService(
            "Standard Cleaning",
            150.00,
            {"Oven Interior": 25.00, "Baseboards": 20.00},
        )

    def test_customer_dictionary(self):
        self.assertEqual(self.customer.to_dict()["name"], "Maria Lopez")

    def test_service_price_without_add_ons(self):
        self.assertEqual(self.service.calculate_price(), 150.00)

    def test_service_price_with_add_ons(self):
        self.assertEqual(
            self.service.calculate_price(["Oven Interior", "Baseboards"]),
            195.00,
        )

    def test_appointment_total_and_cancel(self):
        appointment = Appointment(
            1, self.customer, self.service, "2026-10-10", "10:30 AM", ["Oven Interior"]
        )
        self.assertTrue(appointment.validate_schedule())
        self.assertEqual(appointment.calculate_total(), 175.00)
        appointment.cancel_appointment()
        self.assertEqual(appointment.status, "Canceled")

    def test_invalid_schedule(self):
        appointment = Appointment(
            1, self.customer, self.service, "October 10", "morning"
        )
        with self.assertRaises(ValueError):
            appointment.validate_schedule()


if __name__ == "__main__":
    unittest.main()
