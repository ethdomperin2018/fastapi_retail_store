# Database --> Dockerfile

FROM python:3.9.12-alpine3.15

COPY . /Backend

WORKDIR /Backend/Requirements
# Run poetry install on this folder
RUN pip install -r Requirements.back.txt

WORKDIR /Backend

EXPOSE 8000

CMD ["uvicorn", "Backend:app", "--host", "0.0.0.0", "--port", "8000" , "--reload"]