from datetime import datetime

def obtener_fecha(prompt):
    while True:
        fecha = input(prompt)
        try:
            # Validar formato de fecha ISO 8601
            datetime.fromisoformat(fecha.replace("Z", "+00:00"))
            return fecha
        except ValueError:
            print("Formato de fecha inválido. Usa YYYY-MM-DDTHH:MM:SSZ")
