FROM image_with_python3.9

WORKDIR /jouerflux-docker

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENV INIT_DB TRue

CMD [ "uvicorn",  "app:conn_app"]