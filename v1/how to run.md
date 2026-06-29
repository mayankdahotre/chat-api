pwd

then copy path

cd path
 
python -m venv venv
.\venv\Scripts\activate

deactivate
 
pip install -r requirements.txt
 
copy .env.example .env
# Edit .env with your Azure OpenAI credentials

uvicorn main:app --reload --port 8000