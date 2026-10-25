# Rambla SA: Perfiles de riesgo del inversor uruguayo y carteras modelo

## De qué se trata
Rambla SA es una firma de asesoramiento patrimonial de Montevideo que atiende a unos 640 clientes. El gerente de asesoramiento quiere analizar la brecha entre lo que los clientes dicen que son en una encuesta de perfilado y lo que realmente hacen con su dinero según sus operaciones históricas. El problema principal es que existen desajustes importantes: clientes que se declaran agresivos pero tienen carteras conservadoras (un problema comercial de clientes insatisfechos con el rendimiento) y clientes que se declaran conservadores pero tienen carteras agresivas (un problema legal grave por falta de idoneidad y riesgo ante caídas de mercado). A partir de los datos, limpié la base, evalué la consistencia de las carteras y diseñé un nuevo sistema de perfilado objetivo con carteras modelo adaptadas al mercado uruguayo.

## Los datos
Los datos fueron provistos por la firma con fecha de corte al **30 de junio de 2026**, cubriendo operaciones entre 2024 y 2026 e indicadores macroeconómicos. Para correr el proyecto, los cuatro archivos deben colocarse dentro de la carpeta `datos/` (ignorada por `.gitignore`):

- **`encuesta_inversores.csv`**: 657 respuestas con datos demográficos (`edad`, `sexo`, `ocupacion`, `nivel_educativo`), situación patrimonial (`ingreso_mensual_liquido`, `patrimonio_invertible_usd`, `tiene_deudas`, `tiene_fondo_emergencia`, `meses_gastos_cubiertos`), conocimientos (`anios_experiencia_invirtiendo`, `puntaje_test_conocimiento`, `conocimiento_autopercibido`), perfil declarado (`perfil_autodeclarado`), reacción ante caídas (`reaccion_caida_20`) y expectativas (`retorno_esperado_anual`, `horizonte_inversion`).
- **`movimientos_cartera.csv`**: 4.481 operaciones de compra y suscripción (`id_movimiento`, `id_cliente`, `id_instrumento`, `fecha_operacion`, `tipo_operacion`, `moneda`, `monto`), expresadas en UYU, USD y UI.
- **`catalogo_instrumentos.csv`**: 14 instrumentos disponibles en Uruguay (`nombre_instrumento`, `categoria`, `moneda`, `inversion_minima`, `retorno_anual_historico`, `volatilidad_anual`, `nivel_riesgo`, `liquidez`).
- **`tasas_referencia.csv`**: Valores macroeconómicos al corte: tipo de cambio UYU/USD (42.80), valor de la UI (6.55), inflación de Uruguay (5.4%), inflación de EE.UU. (2.7%), TPM del BCU (8.75%) y tasa de bonos del Tesoro de EE.UU. (4.1%).

## Cómo se instala
Para preparar el entorno de trabajo, abrí una terminal en la carpeta raíz del proyecto y ejecuta:

```bash
# 1. Crear el entorno virtual
python -m venv .venv

# 2. Activar el entorno virtual
# En Windows (PowerShell):
.venv\Scripts\Activate.ps1
# En Windows (cmd):
.venv\Scripts\activate.bat
# En macOS / Linux:
source .venv/bin/activate

# 3. Instalar las dependencias fijadas
pip install -r requirements.txt

# 4. Registrar el kernel para Jupyter y VS Code
python -m ipykernel install --user --name progII --display-name "Python (progII)"
```

## Cómo se ejecuta el proyecto
La estructura del proyecto organiza el código en carpetas limpias:

```text
Proyecto C/
├── README.md                 # Explicación del proyecto y reproducción
├── requirements.txt           # Librerías necesarias con versiones exactas
├── .gitignore                 # Archivos que no van al repositorio (datos y entorno)
├── datos/                     # Archivos CSV crudos
├── notebooks/
│   └── proyecto_final.ipynb   # Notebook con el análisis paso a paso
├── salidas/                   # Gráficos y tablas exportadas
└── src/
    ├── carga.py               # Funciones para verificar y leer los datos
    └── analisis.py            # Constantes y funciones para los cálculos
```

1. Abrí la carpeta raíz `Proyecto C` en **VS Code** o **Jupyter Lab**.
2. Abrí el archivo [`notebooks/proyecto_final.ipynb`](file:///c:/Users/fdesouza/Desktop/Semestre%20II%202026/Programación%20Analítica%20II/Proyecto%20C/notebooks/proyecto_final.ipynb).
3. Seleccioná el kernel `Python (progII)`.
4. Corré las celdas en orden de arriba hacia abajo (*Restart Kernel and Run All Cells*). Las funciones auxiliares se importan automáticamente desde la carpeta `src/`.

## Qué se concluyó
1. **La autodeclaración no refleja la realidad**: Una parte importante de los clientes tiene una cartera que no coincide con su perfil autodeclarado. Encontré clientes que se dicen conservadores pero tienen posiciones de alto riesgo (lo que representa un riesgo regulatorio y legal para la firma ante caídas del mercado) y clientes que se dicen agresivos pero tienen su dinero estancado en renta fija de bajo rendimiento (un problema comercial de clientes que se pueden ir insatisfechos).
2. **Los que no declaran patrimonio son los que más tienen**: Los valores faltantes en ingreso y patrimonio no son aleatorios. Al cruzar los clientes de la encuesta con sus operaciones reales en `movimientos_cartera.csv`, comprobé que la mediana de inversión de quienes no contestaron el patrimonio es de USD 31.078, frente a USD 19.526 de los que sí contestaron (un 59% más alta). Omiten el dato por privacidad, por lo que borrar esas filas o imputarles el promedio hubiera distorsionado a los mejores clientes de la firma.
3. **Expectativas inviables y costo de tener dólares parados**: Varios clientes esperan rentabilidades de dos dígitos mientras mantienen instrumentos conservadores o saldos ociosos en cuenta. Esos dólares sin invertir pierden poder de compra constante frente a la inflación de Estados Unidos (2.7% anual).
4. **Perfilado por comportamiento y carteras modelo**: El perfil del cliente debe construirse a partir de su situación financiera objetiva (fondo de emergencia, meses de gastos cubiertos, horizonte y experiencia real) en lugar de una pregunta de autopercepción. Con los 14 instrumentos del catálogo armé carteras modelo equilibradas que respetan la liquidez y los montos mínimos de entrada.
