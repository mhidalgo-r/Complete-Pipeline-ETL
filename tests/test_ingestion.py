import pytest
import os
from scripts.ingestion.ingest_data import validar_archivo

def test_archivo_no_existe():
    with pytest.raises(FileExistsError):
        validar_archivo("data/raw/no_existe.csv")
    
def test_archivo_existe():
    validar_archivo("data/raw/ventas_sucias.csv")

def test_archivo_vacio(tmp_path):
    archivo_vacio = tmp_path / "vacio.csv"
    archivo_vacio.write_text("vacio")
    with pytest.raises(ValueError):
        validar_archivo(str(archivo_vacio))