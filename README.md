# Установка 

1. git clone https://github.com/fatrunner-39/fastapi_homework.git
2. cd fastapi_homework 
3. python -m venv venv
4. source venv/bin/activate (for windows venv\Scripts\activate) 
5. pip install -r requirements.txt 
6. createdb -U postgres fas_db  
7. uvicorn main:app --reload  
