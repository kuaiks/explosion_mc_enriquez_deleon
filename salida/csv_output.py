import csv
from dominio.puertos import PuertoObservador

# implementa el patrón observador

class SalidaCSV(PuertoObservador):
    
    def __init__(self, archivo="resultados.csv"): # el nombre del archivo CSV donde se guardarán los resultados
        self.archivo = archivo # para guardar el nombre del archivo 
        self.resultados = [] # para acumular resultados durante la simulación antes de escribirlos todos al final

    # Definimos cabeceras claras que abarcan las condiciones para el CSV

    def al_iniciar(self, config): # al iniciar la simulación, preparamos el archivo CSV escribiendo las cabeceras. Esto asegura que cada vez que se ejecute la simulación, el archivo se sobrescriba con los nuevos resultados y no se mezclen con los anteriores.
        self.resultados = [] # reiniciamos la lista de resultados al iniciar una nueva simulación y no se junten con los anteriores.
        with open(self.archivo, 'w', newline='') as f: 
            writer = csv.writer(f) 
            writer.writerow([
                "angulo_deg", "v0", "masa", 
                "alcance", "altura_max", "tiempo_vuelo",
                "energia_inicial", "energia_final", "error_energia"
            ])
    

    # guardamos el resultado rápidamente en una lista

    def al_aterrizar(self, resultado): # cada vez que un proyectil aterriza, se llama a este método con el resultado del proyectil
        self.resultados.append(resultado) # acumulamos el resultado en la lista para escribirlo al final, esto es más eficiente que abrir y escribir en el archivo cada vez que un proyectil aterriza.
    
    def al_finalizar(self, resultados):
        with open(self.archivo, 'a', newline='') as f: 
            writer = csv.writer(f) 
            for r in self.resultados: 
                writer.writerow([
                    r.angulo_deg, r.v0, r.masa,
                    r.alcance, r.altura_max, r.tiempo_vuelo,
                    r.energia_inicial, r.energia_final, r.error_energia
                ]) 
        print(f"Resultados guardados en {self.archivo}") 