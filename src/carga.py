"""Funciones de carga y lectura de datos para el proyecto Rambla SA."""

from pathlib import Path
import pandas as pd

# Carpeta predeterminada de datos
CARPETA_DATOS = Path("datos")

# Archivos del caso
ARCHIVOS_DEFAULT = {
    "encuesta_inversores": "encuesta_inversores.csv",
    "movimientos_cartera": "movimientos_cartera.csv",
    "catalogo_instrumentos": "catalogo_instrumentos.csv",
    "tasas_referencia": "tasas_referencia.csv",
}


def verificar_archivo(nombre_archivo: str, carpeta_datos: Path = CARPETA_DATOS) -> Path:
    # Archivo de encuesta de inversores
    ruta = carpeta_datos / nombre_archivo

    if not ruta.exists():
        ruta = Path("./csv/") / nombre_archivo

    # Verificar exitencia
    if ruta.exists():
        return ruta

    raise FileNotFoundError(
        f"No se encontró el archivo '{nombre_archivo}'. Verificá que esté en datos/."
    )


def cargar_archivo(
    nombre_archivo: str,
    carpeta_datos: Path = CARPETA_DATOS,
    parse_dates: list = None,
) -> pd.DataFrame:
    """Lee un CSV verificando que exista y parseando fechas si corresponde."""
    ruta = verificar_archivo(nombre_archivo, carpeta_datos)
    return pd.read_csv(ruta, parse_dates=parse_dates)


def cargar_datos(
    archivos: dict = None,
    carpeta_datos: Path = CARPETA_DATOS,
) -> dict:
    """Carga los 4 archivos del proyecto con sus tipos y fechas declaradas."""
    if archivos is None:
        archivos = ARCHIVOS_DEFAULT

    fechas_por_archivo = {
        "encuesta_inversores": ["fecha_respuesta"],
        "movimientos_cartera": ["fecha_operacion"],
        "tasas_referencia": ["fecha"],
    }

    datos = {}
    for clave, nombre in archivos.items():
        parse_dates = fechas_por_archivo.get(clave, None)
        datos[clave] = cargar_archivo(
            nombre, carpeta_datos=carpeta_datos, parse_dates=parse_dates
        )

    return datos


def obtener_tasas_referencia(
    carpeta_datos: Path = CARPETA_DATOS,
) -> tuple:
    """Obtiene el tipo de cambio USD/UYU y el valor de la UI de tasas_referencia.csv."""
    tc_uyu = 42.80
    val_ui = 6.55
    try:
        df_tasas = cargar_archivo("tasas_referencia.csv", carpeta_datos)
        es_dolar = df_tasas["concepto"].str.contains(
            "dólar", case=False, na=False
        )
        fila_tc = df_tasas[es_dolar]
        if not fila_tc.empty:
            tc_uyu = float(fila_tc["valor"].iloc[0])

        es_ui = df_tasas["concepto"].str.contains(
            "Unidad Indexada", case=False, na=False
        )
        fila_ui = df_tasas[es_ui]
        if not fila_ui.empty:
            val_ui = float(fila_ui["valor"].iloc[0])
    except Exception:
        pass

    return tc_uyu, val_ui
