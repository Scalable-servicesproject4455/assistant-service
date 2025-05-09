# # s2/Dockerfile
FROM python:3.10-slim
 
WORKDIR /app
 
COPY . .
 
RUN pip install flask pika mysql-connector-python
 
CMD ["python", "app.py"]