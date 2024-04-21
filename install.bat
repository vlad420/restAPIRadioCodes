@echo off

REM Verifică dacă mediul virtual există și îl creează dacă nu există
IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
) ELSE (
    echo Virtual environment already exists.
)

REM Activează mediul virtual
echo Se activeaza mediul virtual...
call venv\Scripts\activate

REM Instalează dependențele
echo Instalare dependente din requirements.txt...
pip install -r requirements.txt

echo Instalarea s-a completat cu succes!
