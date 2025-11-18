#Dockerfile
FROM python:3.12.9-slim
WORKDIR /root

#install requirements
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./
RUN mkdir output
RUN python src/read_data.py
RUN python src/text_preprocessing.py
RUN python src/text_classification.py

COPY . ./

ENTRYPOINT [ "python", "src/serve_model.py" ]
