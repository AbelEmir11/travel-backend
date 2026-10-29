import unittest
from datetime import date, timedelta
from app import create_app
from config import TestingConfig
from models import db, Usuario, Alojamiento, Reserva

class TestReservasEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Crear usuario cliente de prueba
        reg = self.client.post("/api/autenticacion/registro", json={
            "nombre": "Tester Cliente",
            "email": "tester@test.com",
            "password": "password123"
        })
        self.token = reg.get_json()["token"]
        self.usuario_id = reg.get_json()["usuario"]["id"]

        # Crear alojamiento de prueba
        self.alojamiento = Alojamiento(
            id="hotel-patagonia-test",
            titulo="Hotel Patagonia Test",
            ubicacion="Bariloche",
            provincia="Rio Negro",
            precio=100,
            tipo="estadia",
            experience_label="Estadia de Lujo",
            descripcion="Hermoso hotel de prueba frente al lago.",
            destacado=True,
            activo=True,
            descuento=10
        )
        self.alojamiento.imagenes = ["https://example.com/img1.jpg"]
        db.session.add(self.alojamiento)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_creacion_reserva_exitosa(self):
        check_in = (date.today() + timedelta(days=10)).isoformat()
        check_out = (date.today() + timedelta(days=15)).isoformat()

        payload = {
            "alojamiento_id": "hotel-patagonia-test",
            "check_in": check_in,
            "check_out": check_out,
            "huespedes": 2,
            "notes": "Llegada por la tarde"
        }
        res = self.client.post("/api/reservas", json=payload, headers={
            "Authorization": f"Bearer {self.token}"
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertIn("reserva", data)
        self.assertEqual(data["reserva"]["estado"], "pending")
        # 5 noches * $90 (10% off sobre $100) + $40 servicio = $490
        self.assertEqual(data["reserva"]["precio_total"], 490)

    def test_overbooking_fechas_solapadas_rechazadas(self):
        # 1. Crear primera reserva del dia +20 al dia +25
        check_in_1 = (date.today() + timedelta(days=20)).isoformat()
        check_out_1 = (date.today() + timedelta(days=25)).isoformat()

        res1 = self.client.post("/api/reservas", json={
            "alojamiento_id": "hotel-patagonia-test",
            "check_in": check_in_1,
            "check_out": check_out_1,
            "huespedes": 2
        }, headers={"Authorization": f"Bearer {self.token}"})
        self.assertEqual(res1.status_code, 201)

        # 2. Intentar reservar un rango que se solapa (ej. del dia +22 al dia +27)
        check_in_solapado = (date.today() + timedelta(days=22)).isoformat()
        check_out_solapado = (date.today() + timedelta(days=27)).isoformat()

        res2 = self.client.post("/api/reservas", json={
            "alojamiento_id": "hotel-patagonia-test",
            "check_in": check_in_solapado,
            "check_out": check_out_solapado,
            "huespedes": 1
        }, headers={"Authorization": f"Bearer {self.token}"})

        # Debe responder 409 Conflict por sobre-reserva / solapamiento
        self.assertEqual(res2.status_code, 409)
        data = res2.get_json()
        self.assertIn("error", data)
        self.assertIn("reserva activa", data["error"])

    def test_cancelacion_reserva(self):
        check_in = (date.today() + timedelta(days=30)).isoformat()
        check_out = (date.today() + timedelta(days=32)).isoformat()

        res = self.client.post("/api/reservas", json={
            "alojamiento_id": "hotel-patagonia-test",
            "check_in": check_in,
            "check_out": check_out,
            "huespedes": 1
        }, headers={"Authorization": f"Bearer {self.token}"})
        reserva_id = res.get_json()["reserva"]["id"]

        # Cancelar
        cancel_res = self.client.put(f"/api/reservas/{reserva_id}/cancelar", headers={
            "Authorization": f"Bearer {self.token}"
        })
        self.assertEqual(cancel_res.status_code, 200)
        self.assertEqual(cancel_res.get_json()["reserva"]["estado"], "cancelled")

if __name__ == "__main__":
    unittest.main()
