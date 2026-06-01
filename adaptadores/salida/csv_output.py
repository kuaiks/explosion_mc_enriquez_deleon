import csv
from dominio.puertos import PuertoObservador

# implementa el patrón observador

class SalidaCSV(PuertoObservador):
    
    def __init__(self, archivo="resultados.csv"):
        self.archivo = archivo
        self.resultados = []

    # Definimos cabeceras claras que abarcan las condiciones para el CSV

    def al_iniciar(self, config):
        self.resultados = []
        with open(self.archivo, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "angulo_deg", "v0", "masa", 
                "alcance", "altura_max", "tiempo_vuelo",
                "energia_inicial", "energia_final", "error_energia"
            ])
    

    # guardamos el resultado rápidamente en una lista

    def al_aterrizar(self, resultado):
        """Acumula resultado (se guardará al final)."""
        self.resultados.append(resultado)
    
    def al_finalizar(self, resultados):
        """Guarda todos los resultados en CSV."""
        with open(self.archivo, 'a', newline='') as f:
            writer = csv.writer(f)
            for r in self.resultados:
                writer.writerow([
                    r.angulo_deg, r.v0, r.masa,
                    r.alcance, r.altura_max, r.tiempo_vuelo,
                    r.energia_inicial, r.energia_final, r.error_energia
                ])
        print(f"✅ Resultados guardados en {self.archivo}")