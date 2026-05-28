import pandas as pd
from pathlib import Path 
import os
import logging
import chardet
import hashlib
import csv
import numpy as np

# ============================================================
# SCRIPT DE INGESTA
# Entrada : data/raw/ventas_sucias.csv
# Salida  : DataFrame en memoria para clean_data.py
# ============================================================

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler("logs/ingest_logs.txt",encoding="utf-8"),
            logging.StreamHandler()
        ]
    )


# PASO 1 — Validar si el archivo existe y no está vacío
def validar_archivo(ruta_archivo : str ) -> None: # definir funcion llamada validar_archivo(recibe variable ruta_archivo de tipo : string) y -> devuelve nada None

    ruta = Path(ruta_archivo)
    if not ruta.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {ruta}")
    if ruta.stat().st_size == 0:
        raise ValueError(f"Archivo vacío: {ruta}")# si esta vacio error y para el pipeline con value error
    
    logging.info("El archivo existe") #logging de que funciono 




# PASO 2 — Detectar encoding
def detectar_encoding(ruta_archivo: str) -> str:
    with open(ruta_archivo, "rb") as f:
        result_encode = chardet.detect(f.read(10000))
    encoding = result_encode["encoding"]
    confianza = result_encode["confidence"]
    if not encoding:
        raise ValueError(f"no se pudo detectar el encodig en {ruta_archivo}")
    if confianza < 0.7:
        logging.warning(f"Confianza baja en la deteccion de encoding: {confianza:.0%}")

    logging.info(f"enconding detectado: {encoding} | Nivel de confianza: {confianza:.0%}")
    return encoding

# PASO 3 — Detectar separador
def detectar_separador(ruta_archivo: str, encoding: str) -> str:
    with open(ruta_archivo, "r",encoding=encoding) as f:
        muestra = f.read(2048)
    try:
        dialect = csv.Sniffer().sniff(muestra)
        separador= dialect.delimiter
    except csv.Error:
        logging.warning(f"no se pudo detectar el separador por defecto")
        separador=","
    separador_permitido = [",",";","|","\t"]
    if separador not in separador_permitido:
        logging.warning(f"separador encontrado no valido")
    logging.info(f"el separador encontado es '{separador}'")
    return separador

# PASO 4 — Generar huella MD5
def calcular_checksum(ruta_archivo: str) -> str:
    with open (ruta_archivo,"rb") as f:
        hash_sha=hashlib.sha256()
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha.update(chunk)
        checksum = hash_sha.hexdigest()
    logging.info(f"se genero el checksum del archivo con la clave {checksum}")
    return checksum


# PASO 5 — Leer el archivo con pandas
def leer_csv(ruta_archivo: str, encoding: str, separador: str) -> pd.DataFrame:
        df = pd.read_csv(
            ruta_archivo,
            encoding=encoding,
            sep=separador,
            dtype=str,
            skipinitialspace=True
        )
        df.columns = df.columns.str.strip().str.lower()
        df = df.replace("",np.nan)
        
        logging.info(f"archivo cargado {df.shape[0]} filas | {df.shape[1]} columnas")
        logging.info(f"columnas encontrada {list(df.columns)}")
        return df



# PASO 6 — Validar las columnas
def validar_columnas(df: pd.DataFrame, columnas_esperadas: list) -> None:
    columnas_encontradas = set(df.columns)
    set_esperadas        = set(columnas_esperadas)
    faltantes            = set_esperadas - columnas_encontradas
    extras               = columnas_encontradas - set_esperadas

    if faltantes:
        raise ValueError(f"Columnas faltantes: {faltantes}")

    if extras:
        logging.warning(f"Columnas extra encontradas: {extras}")

    logging.info("Columnas validadas correctamente")


# PASO 7 — Registrar metadatos en el log
def registrar_metadata(ruta_archivo: str, encoding: str, 
                       separador: str, checksum: str, 
                       df: pd.DataFrame) -> None:
    logging.info("=" * 50)
    logging.info("RESUMEN DE INGESTA")
    logging.info("=" * 50)
    logging.info(f"Archivo    : {ruta_archivo}")
    logging.info(f"Encoding   : {encoding}")
    logging.info(f"Separador  : '{separador}'")
    logging.info(f"Checksum   : {checksum}")
    logging.info(f"Filas      : {df.shape[0]}")
    logging.info(f"Columnas   : {df.shape[1]}")
    logging.info(f"Nombres    : {list(df.columns)}")
    logging.info("=" * 50)


# PASO 8 — Ingestar: orquesta todo
def ingestar(ruta_archivo:str)->pd.DataFrame:

    columnas_esperadas = [
    "id", "nombre", "edad", 
    "ciudad", "fecha_compra", 
    "monto", "metodo_pago"
    ]

    validar_archivo(ruta_archivo)
    #    ↑ no devuelve nada, solo valida

    encoding = detectar_encoding(ruta_archivo)
    #    ↑ devuelve "utf-8"
    #    ↓ se lo pasa a detectar_separador

    separador = detectar_separador(ruta_archivo, encoding)
    #    ↑ devuelve ","
    #    ↓ se lo pasa a leer_csv

    checksum = calcular_checksum(ruta_archivo)
    #    ↑ devuelve "a3f4b2c1..."

    df = leer_csv(ruta_archivo, encoding, separador)
    #    ↑ devuelve el DataFrame completo


    validar_columnas(df, columnas_esperadas)
    #    ↑ no devuelve nada, solo valida

    registrar_metadata(ruta_archivo, encoding, separador, checksum, df)
    #    ↑ no devuelve nada, solo registra

    return df
    #    ↑ entrega el DataFrame a main()


# PASO 9 — Main: punto de entrada
def main()->None:
    try:
        ruta_archivo="data/raw/ventas_sucias.csv"
        df=ingestar(ruta_archivo)
    except FileNotFoundError as e:
        logging.error(f"Error: Archivo no encontrado {e}")
    except ValueError as e:
        logging.error(f"Error: Error de validacion {e}")
    except Exception as e:
        logging.exception(f"Error inesperado en el pipeline {e}")
    
    
    


if __name__ == "__main__":
    main()