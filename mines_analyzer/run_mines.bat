@echo off
echo Installing requirements...
if exist mines_analyzer (
    cd mines_analyzer
)

python -m pip install -r requirements.txt

echo Starting Mines Analyzer AI...
python -m streamlit run app.py
pause
