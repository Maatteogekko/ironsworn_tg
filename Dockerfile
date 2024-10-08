FROM python:3.12.4
WORKDIR /usr/src/app
COPY . .
RUN pip install -r requirements.txt 
CMD ["python", "main.py"]