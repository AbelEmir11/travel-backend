from app import app

if __name__ == "__main__":
    # Correr el servidor Flask en el puerto 5000 de desarrollo local
    app.run(port=5000, debug=True)
