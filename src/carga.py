# Script con funciones para leer y limpiar

"""Lectura de la cartera de créditos de FinCo."""

import csv

# Pesos uruguayos por dólar al 30/06/2026, fecha de corte de los datos
TIPO_DE_CAMBIO_DE_CORTE = 41.5


def cargar_cartera(ruta_archivo):
    """Lee el CSV de la cartera y agrega el monto expresado en pesos.

    El monto viene en la moneda del contrato, así que sin convertir no se puede sumar.
    """
    creditos = []
    with open(ruta_archivo, encoding="utf-8") as archivo:
        for fila in csv.DictReader(archivo):
            fila["monto_otorgado"] = float(fila["monto_otorgado"])
            fila["dias_atraso"] = int(fila["dias_atraso"])
            if fila["moneda"] == "USD":
                fila["monto_en_pesos"] = fila["monto_otorgado"] * TIPO_DE_CAMBIO_DE_CORTE
            else:
                fila["monto_en_pesos"] = fila["monto_otorgado"]
            creditos.append(fila)
    return creditos