import pandas as pd
import logging
import numpy as np


def limpiar_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    
    filas_antes = len(df)

    df = df.drop_duplicates(keep="first")

    filas_despues = len(df)
    
    duplicados=filas_antes-filas_despues

    if filas_despues == 0 :
        logging.warning("El archivo quedo vacio luego de la limpieza")
    
    elif duplicados > 0:
        logging.info(
            f"dulplicados eliminados {duplicados} |"
            f"filas Antes de la limpieza {filas_antes} |"
            f"filas Despues de la limpieza {filas_despues}"
        )  
    else:
        logging.info("no se han encontrado duplicados")
    return  df

def limpieza_de_nulos(df: pd.DataFrame) ->pd.DataFrame:
    
    total_nulos = df.isna().sum().sum()
    nulos_por_columnas = df.isna().sum()
    logging.info(f"La cantidad de nulos totales es {total_nulos}")
    logging.info(f"La cantidad de nulos por columna es {nulos_por_columnas}")
    columnas_criticas = ["id", "nombre", "fecha_compra", "monto"]
    df = df.dropna(subset=columnas_criticas)


    edad_numerica = pd.to_numeric(df["edad"], errors="coerce")

    mediana_edad = edad_numerica.where(
        edad_numerica.between(0,110), other=np.nan
    )
    edad_numerica = edad_numerica.median()

    df["edad"] = edad_numerica.fillna(mediana_edad)

    logging.info(f"Columna nulas de 'Edad' imputadas con {mediana_edad}")

    for col in ["ciudad","metodo_pago"]:
        nulos = df[col].isna().sum()
        df[col] = df[col].fillna("Desconocido")
        logging.info(f"columna: {col} - {nulos} nulos imputados con 'Desconocido'")
    
    nulos_despues = df.isna().sum().sum()
    logging.info(f"Nulos restantes despues de limpieza : {nulos_despues}")
    return df

def limpiar_tipos(df: pd.DataFrame) -> pd.DataFrame:
    # registrar tipos antes
    logging.info(f"Tipos antes de conversión:\n{df.dtypes}")

    # id → Int64
    df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
    if df["id"].isna().sum() > 0:
        logging.warning(f"'id' — {df['id'].isna().sum()} valores no convertibles")

    # edad → Int64
    df["edad"] = pd.to_numeric(df["edad"], errors="coerce").astype("Int64")

    # monto → float
    df["monto"] = pd.to_numeric(df["monto"], errors="coerce")
    if df["monto"].isna().sum() > 0:
        logging.warning(f"'monto' — {df['monto'].isna().sum()} valores no convertibles")

    # fecha → string normalizado YYYY-MM-DD
    df["fecha_compra"] = pd.to_datetime(
        df["fecha_compra"],
        errors="coerce",
        dayfirst=True
    ).dt.strftime("%Y-%m-%d")
    if df["fecha_compra"].isna().sum() > 0:
        logging.warning(f"'fecha_compra' — {df['fecha_compra'].isna().sum()} fechas inválidas")

    # registrar tipos después
    logging.info(f"Tipos después de conversión:\n{df.dtypes}")

    return df