"""Constantes y funciones de análisis para el proyecto Rambla SA."""

import pandas as pd
from IPython.display import Markdown, display

# Constantes de configuración

# Fecha de corte del caso
FECHA_DE_CORTE = "2026-06-30"

# Tipo de cambio peso uruguayo por dólar al 30/06/2026
TIPO_DE_CAMBIO_DE_CORTE = 42.80

# Valor en pesos de la Unidad Indexada al 30/06/2026
VALOR_UI_DE_CORTE = 6.55

# Marcadores de no respuesta en la encuesta
MARCADORES_NO_RESPUESTA = [
    "prefiero no contestar",
    "s/d",
    "n/c",
    "ns/nc",
    "no sabe",
    "no contesta",
    "-",
    "?",
    "",
]

# Valores numéricos usados como centinela de no respuesta
VALORES_CENTINELA = [-999, -99, 999, 9999]

# Rangos válidos para detectar valores imposibles
RANGOS_VALIDOS = {
    "edad": (18, 100),
    "ingreso_mensual_liquido": (0, float("inf")),
    "patrimonio_invertible_usd": (0, float("inf")),
    "meses_gastos_cubiertos": (0, float("inf")),
    "anios_experiencia_invirtiendo": (0, float("inf")),
    "puntaje_test_conocimiento": (0, 10),
    "conocimiento_autopercibido": (1, 5),
    "monto": (0, float("inf")),
}

# Colores para gráficos
COLORES_PERFILES = {
    "Conservador": "#2E86AB",
    "Moderado": "#E8A33D",
    "Agresivo": "#BB3300",
}

# Funciones de calidad y análisis (Etapa 1)


def mostrar_primeras_filas(nombre: str, datos: pd.DataFrame, n: int = 5) -> None:
    """Muestra el nombre del archivo y sus primeras filas."""
    display(Markdown(f"### **Archivo: `{nombre}.csv`**"))
    display(datos.head(n))


def mostrar_descripcion(datos: pd.DataFrame) -> None:
    """Muestra filas, columnas, tipos de datos y resumen estadístico."""
    filas, columnas = datos.shape
    display(Markdown(f"**Dimensiones:** {filas:,} filas × {columnas} columnas"))

    display(Markdown("#### Tipos de dato"))
    display(datos.dtypes.to_frame(name="tipo_dato").T)

    categoricas = datos.select_dtypes(include=["object", "category", "string", "bool"])
    if not categoricas.empty:
        display(Markdown("#### Categorías por columna categórica"))
        display(categoricas.nunique().to_frame(name="cantidad_categorias"))

    continuas = datos.select_dtypes(include="number")
    if not continuas.empty:
        display(Markdown("#### Resumen de variables numéricas"))
        display(continuas.describe().T)


def mostrar_duplicados(datos: pd.DataFrame) -> None:
    """Busca duplicados exactos, de cliente y de operaciones."""
    exactos = datos.duplicated()
    display(Markdown(f"**Duplicados exactos:** {exactos.sum()} filas"))
    if exactos.any():
        cols = list(datos.columns)
        display(datos[exactos].sort_values(cols).head(10))

    # Formularios enviados dos veces por un mismo cliente
    if "id_cliente" in datos.columns and "id_movimiento" not in datos.columns:
        repetidos = datos[datos.duplicated(subset="id_cliente", keep=False)]
        cant_sobrantes = datos.duplicated(subset="id_cliente").sum()
        display(
            Markdown(
                f"**Formularios con id_cliente repetido:** {cant_sobrantes} de más "
                f"({len(repetidos)} filas en total)"
            )
        )
        if not repetidos.empty:
            display(repetidos.sort_values("id_cliente").head(10))

    # Operaciones duplicadas (mismas columnas ignorando id_movimiento)
    if "id_movimiento" in datos.columns:
        clave = [c for c in datos.columns if c != "id_movimiento"]
        ops_rep = datos[datos.duplicated(subset=clave, keep=False)]
        cant_ops = datos.duplicated(subset=clave).sum()
        display(
            Markdown(
                f"**Operaciones repetidas (sin id_movimiento):** {cant_ops} filas "
                f"({len(ops_rep)} involucradas)"
            )
        )
        if not ops_rep.empty:
            display(ops_rep.sort_values(clave).head(10))


def mostrar_faltantes(datos: pd.DataFrame) -> None:
    """Muestra cantidad y porcentaje de valores nulos (isna)."""
    faltantes = datos.isna().sum()
    pct = (datos.isna().mean() * 100).round(2)
    resumen = pd.DataFrame({"faltantes": faltantes, "porcentaje": pct})
    resumen = resumen[resumen["faltantes"] > 0].sort_values(
        "faltantes", ascending=False
    )

    display(Markdown("#### Faltantes por columna (`isna()`)"))
    if resumen.empty:
        display(Markdown("No hay valores nulos en esta tabla."))
        return
    display(resumen)

    for columna in resumen.index[:3]:
        filas = datos[datos[columna].isna()]
        display(
            Markdown(
                f"Ejemplo de `{columna}` faltante: {len(filas)} filas (primeras 3):"
            )
        )
        display(filas.head(3))


def mostrar_valores_raros(datos: pd.DataFrame) -> None:
    """Detecta texto en numéricas, fechas inválidas y no respuesta disfrazada."""
    textos = datos.select_dtypes(exclude="number").columns
    fechas = [c for c in textos if c.startswith("fecha")]

    # Texto en columnas numéricas
    for columna in textos:
        if columna in fechas:
            continue
        valores = datos[columna].dropna().astype(str)
        es_numero = valores.str.fullmatch(r"\s*\$?\s*-?\d+([.,]\d+)*\s*")
        if valores.empty or es_numero.mean() < 0.5:
            continue
        raros = valores[~es_numero]
        display(Markdown(f"`{columna}` tiene **{len(raros)}** valores no numéricos"))
        display(raros.value_counts().to_frame(name="frecuencia"))

    # Fechas no parseables
    for columna in fechas:
        valores = datos[columna].dropna().astype(str)
        raros = valores[pd.to_datetime(valores, errors="coerce", format="mixed").isna()]
        if not raros.empty:
            display(Markdown(f"`{columna}` tiene **{len(raros)}** fechas inválidas"))

    # Formas de no respuesta encubiertas
    resumen = []
    for columna in datos.columns:
        if columna.startswith("id_"):
            continue
        if columna in textos:
            txt_limpio = datos[columna].astype(str).str.strip().str.lower()
            disfrazados = txt_limpio.isin(MARCADORES_NO_RESPUESTA)
        else:
            disfrazados = datos[columna].isin(VALORES_CENTINELA)

        if disfrazados.any():
            nulos = int(datos[columna].isna().sum())
            resumen.append((columna, nulos, int(disfrazados.sum())))

    display(Markdown("#### Formas de decir «no contestó»"))
    if not resumen:
        display(Markdown("No se encontraron respuestas encubiertas."))
        return
    tabla = pd.DataFrame(
        resumen,
        columns=["columna", "nulos_isna", "disfrazados_o_centinelas"],
    ).set_index("columna")
    tabla["total_no_contesto"] = tabla.sum(axis=1)
    display(tabla)


def mostrar_rangos_imposibles(datos: pd.DataFrame) -> None:
    """Busca números fuera de los rangos válidos e incoherencias lógicas."""
    display(Markdown("#### Validación de rangos lógicos"))
    encontrados = 0
    for columna, (minimo, maximo) in RANGOS_VALIDOS.items():
        if columna not in datos.columns:
            continue
        col_num = pd.to_numeric(datos[columna], errors="coerce")
        fuera = col_num.notna() & ~col_num.between(minimo, maximo)
        if fuera.any():
            encontrados += 1
            min_val = col_num.loc[fuera].min()
            max_val = col_num.loc[fuera].max()
            display(
                Markdown(
                    f"`{columna}` fuera de [{minimo}, {maximo}]: "
                    f"**{fuera.sum()}** filas (rango: {min_val} a {max_val})"
                )
            )

    if "edad" in datos.columns and "anios_experiencia_invirtiendo" in datos.columns:
        edad = pd.to_numeric(datos["edad"], errors="coerce")
        exp = pd.to_numeric(datos["anios_experiencia_invirtiendo"], errors="coerce")
        incoherentes = (edad.notna() & exp.notna()) & (exp > edad)
        if incoherentes.any():
            encontrados += 1
            display(
                Markdown(
                    f"`anios_experiencia_invirtiendo` mayor que `edad`: "
                    f"**{incoherentes.sum()}** filas"
                )
            )

    if encontrados == 0:
        display(Markdown("No se encontraron números fuera de rango."))


def mostrar_campos_vacios(datos: pd.DataFrame) -> None:
    """Clasifica los campos vacíos en error de carga o pregunta salteada."""
    display(Markdown("#### Clasificación de campos vacíos"))
    es_encuesta = (
        "id_movimiento" not in datos.columns and "perfil_autodeclarado" in datos.columns
    )

    filas = []
    for columna in datos.columns:
        cantidad = int(datos[columna].isna().sum())
        if cantidad == 0:
            continue

        if not es_encuesta or columna.startswith("id_"):
            tipo = "error de carga"
            tratamiento = "Buscar en otra tabla; si no, dejar NaN"
        else:
            tipo = "salteada por el encuestado"
            tratamiento = "Categoría 'No contesta'; no imputar la media"

        filas.append(
            {
                "columna": columna,
                "tipo": tipo,
                "cantidad": cantidad,
                "tratamiento": tratamiento,
            }
        )

    if not filas:
        display(Markdown("No se encontraron campos vacíos."))
        return

    detalle = pd.DataFrame(filas)
    display(detalle)

    totales = detalle.groupby("tipo", as_index=False).agg(
        total_celdas=("cantidad", "sum"),
        tratamiento=("tratamiento", "first"),
    )
    display(totales)


def validar_faltantes(datos: pd.DataFrame) -> None:
    """Analiza cómo se reparten los faltantes de ingreso y patrimonio."""
    col_ingreso = "ingreso_mensual_liquido"
    col_patrimonio = "patrimonio_invertible_usd"

    if col_ingreso not in datos.columns or col_patrimonio not in datos.columns:
        return

    display(Markdown("### **1.7 Distribución de faltantes: Ingreso y Patrimonio**"))

    ing_txt = datos[col_ingreso].astype(str).str.strip().str.lower()
    ing_no_contesta = ing_txt.isin(MARCADORES_NO_RESPUESTA)
    ing_num = pd.to_numeric(ing_txt, errors="coerce")
    falta_ing = datos[col_ingreso].isna() | ing_no_contesta | (ing_num < 0)
    falta_pat = datos[col_patrimonio].isna() | (datos[col_patrimonio] < 0)

    total = len(datos)
    resumen = pd.DataFrame(
        {
            "nulos_isna": [
                int(datos[col_ingreso].isna().sum()),
                int(datos[col_patrimonio].isna().sum()),
            ],
            "disfrazados_o_centinela": [
                int((falta_ing & datos[col_ingreso].notna()).sum()),
                int((falta_pat & datos[col_patrimonio].notna()).sum()),
            ],
            "total_faltantes": [int(falta_ing.sum()), int(falta_pat.sum())],
            "pct_faltantes": [
                round((falta_ing.sum() / total) * 100, 2),
                round((falta_pat.sum() / total) * 100, 2),
            ],
        },
        index=[col_ingreso, col_patrimonio],
    )
    display(resumen)

    df_trabajo = datos.copy()
    df_trabajo["falta_ingreso"] = falta_ing
    df_trabajo["falta_patrimonio"] = falta_pat

    for agrupador in ["ocupacion", "nivel_educativo"]:
        if agrupador in df_trabajo.columns:
            dist = (
                df_trabajo.groupby(agrupador)
                .agg(
                    total_clientes=("id_cliente", "count"),
                    faltan_ingresos=("falta_ingreso", "sum"),
                    pct_falta_ingreso=(
                        "falta_ingreso",
                        lambda s: round(s.mean() * 100, 2),
                    ),
                    faltan_patrimonio=("falta_patrimonio", "sum"),
                    pct_falta_patrimonio=(
                        "falta_patrimonio",
                        lambda s: round(s.mean() * 100, 2),
                    ),
                )
                .sort_values(by="pct_falta_patrimonio", ascending=False)
            )
            display(Markdown(f"#### Faltantes según `{agrupador}`"))
            display(dist)


def convertir_operaciones_a_usd(
    df_mov: pd.DataFrame,
    tc_uyu: float = TIPO_DE_CAMBIO_DE_CORTE,
    val_ui: float = VALOR_UI_DE_CORTE,
) -> pd.DataFrame:
    """Convierte los montos de movimientos_cartera a USD según su moneda."""
    factores = {"USD": 1.0, "UYU": 1.0 / tc_uyu, "UI": val_ui / tc_uyu}
    df = df_mov.copy()
    df["monto_usd"] = (df["monto"] * df["moneda"].map(factores)).round(2)
    return df


def validar_patrimonio(
    datos_encuesta: pd.DataFrame,
    df_mov: pd.DataFrame,
    tc_uyu: float = TIPO_DE_CAMBIO_DE_CORTE,
    val_ui: float = VALOR_UI_DE_CORTE,
) -> None:
    """Compara el patrimonio declarado contra la cartera real en operaciones."""
    col_patrimonio = "patrimonio_invertible_usd"
    if col_patrimonio not in datos_encuesta.columns:
        return

    display(Markdown("### **1.7 Patrimonio declarado vs. Cartera real**"))

    # Convertir movimientos a USD y sumar por cliente
    df_mov_usd = convertir_operaciones_a_usd(df_mov, tc_uyu, val_ui)
    cartera_cliente = (
        df_mov_usd.groupby("id_cliente", as_index=False)["monto_usd"]
        .sum()
        .rename(columns={"monto_usd": "cartera_real_usd"})
    )

    df_cruce = pd.merge(datos_encuesta, cartera_cliente, on="id_cliente", how="inner")
    df_cruce["no_declaro_patrimonio"] = df_cruce[col_patrimonio].isna() | (
        df_cruce[col_patrimonio] < 0
    )
    df_cruce["estado_patrimonio"] = df_cruce["no_declaro_patrimonio"].map(
        {True: "No contestó", False: "Declaró patrimonio"}
    )

    resumen = (
        df_cruce.groupby("estado_patrimonio")["cartera_real_usd"]
        .agg(
            clientes="count",
            media_usd="mean",
            mediana_usd="median",
            minimo_usd="min",
            maximo_usd="max",
        )
        .round(2)
    )
    display(Markdown("#### Cartera real según si declaró patrimonio"))
    display(resumen)

    df_cruce["quintil_cartera_real"] = pd.qcut(
        df_cruce["cartera_real_usd"],
        q=5,
        labels=["Q1 (Baja)", "Q2", "Q3", "Q4", "Q5 (Alta)"],
    )
    patron_quintiles = (
        df_cruce.groupby("quintil_cartera_real", observed=False)
        .agg(
            total_clientes=("id_cliente", "count"),
            sin_declarar=("no_declaro_patrimonio", "sum"),
            pct_sin_declarar=(
                "no_declaro_patrimonio",
                lambda s: round(s.mean() * 100, 2),
            ),
            monto_promedio_usd=("cartera_real_usd", "mean"),
        )
        .round(2)
    )
    display(Markdown("#### No respuesta por quintil de cartera"))
    display(patron_quintiles)

    med_declara = resumen.loc["Declaró patrimonio", "mediana_usd"]
    med_no_declara = resumen.loc["No contestó", "mediana_usd"]
    dif_pct = round(((med_no_declara - med_declara) / med_declara) * 100, 1)

    texto_conclusion = (
        "> **¿Quién es el que no contesta?**\n"
        "> Los clientes que no declararon patrimonio tienen una cartera real\n"
        f"> con una mediana de **USD {med_no_declara:,.2f}**, que es un "
        f"**{dif_pct}% mayor**\n"
        f"> que la de los que sí declararon (**USD {med_declara:,.2f}**).\n"
        "> La no respuesta se concentra en los quintiles más altos (Q4 y Q5).\n"
        "> Son clientes con patrimonios altos que eligen no contestar por "
        "privacidad.\n"
        ">\n"
        "> **Decisión para el análisis:**\n"
        "> - **No borrar las filas:** borraríamos al segmento con más fondos.\n"
        "> - **No imputar con la media:** subestimaría a los clientes de mayor "
        "patrimonio.\n"
        "> - **Solución:** usamos como patrimonio el dinero que tienen "
        "invertido en la firma\n"
        ">   (`cartera_real_usd`), y guardamos un indicador de que no declararon."
    )
    display(Markdown(texto_conclusion))
