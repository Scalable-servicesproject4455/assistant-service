# s2/Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY serviceTwo.py .

RUN pip install flask requests

EXPOSE 8080
CMD ["python", "serviceTwo.py"]
