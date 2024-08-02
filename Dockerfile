FROM python:3.12.4
WORKDIR /usr/src/app
COPY . .
RUN pip install python-telegram-bot
CMD ["python", "main.py"]