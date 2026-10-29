import unittest
import json
from app import create_app
from config import TestingConfig
from models import db, Usuario

class TestAuthEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_registro_exitoso(self):
        payload = {
            "nombre": "Maria Lopez",
            "email": "maria@test.com",
            "password": "password123"
        }
        res = self.client.post("/api/autenticacion/registro", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertIn("token", data)
        self.assertEqual(data["usuario"]["email"], "maria@test.com")
        self.assertEqual(data["usuario"]["rol"], "cliente")

    def test_registro_email_invalido(self):
        payload = {
            "nombre": "Juan Perez",
            "email": "correo-no-valido",
            "password": "password123"
        }
        res = self.client.post("/api/autenticacion/registro", json=payload)
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("error", data)

    def test_registro_password_corto(self):
        payload = {
            "nombre": "Juan Perez",
            "email": "juan@test.com",
            "password": "123"
        }
        res = self.client.post("/api/autenticacion/registro", json=payload)
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("al menos 6 caracteres", data["error"])

    def test_ingreso_credenciales_correctas(self):
        # Primero registrar
        self.client.post("/api/autenticacion/registro", json={
            "nombre": "Carlos Gomez",
            "email": "carlos@test.com",
            "password": "secretofuerte"
        })
        # Intentar login
        res = self.client.post("/api/autenticacion/ingreso", json={
            "email": "carlos@test.com",
            "password": "secretofuerte"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("token", data)

    def test_ingreso_credenciales_incorrectas(self):
        res = self.client.post("/api/autenticacion/ingreso", json={
            "email": "noexiste@test.com",
            "password": "wrongpassword"
        })
        self.assertEqual(res.status_code, 401)

    def test_obtener_perfil_protegido(self):
        reg = self.client.post("/api/autenticacion/registro", json={
            "nombre": "Ana Suarez",
            "email": "ana@test.com",
            "password": "password123"
        })
        token = reg.get_json()["token"]

        # Acceso con token
        res = self.client.get("/api/autenticacion/perfil", headers={
            "Authorization": f"Bearer {token}"
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["email"], "ana@test.com")

        # Acceso sin token
        res_no_token = self.client.get("/api/autenticacion/perfil")
        self.assertEqual(res_no_token.status_code, 401)

if __name__ == "__main__":
    unittest.main()
