FROM python:3
COPY . /code
WORKDIR /code
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
