
FROM python:3.6.9-slim-stretch
 
WORKDIR /app
ENV PYTHONPATH=/app

RUN apt-get update &&\
    apt-get -y upgrade &&\
    apt-get -y install gcc&&\
    apt-get -y install wget&&\
    apt-get -y install libglib2.0-0&&\
    apt-get -y install libsm6 libxext6 &&\
    apt-get -y install libxrender-dev &&\
    apt-get -y install zip &&\
    apt -y autoremove

COPY requirements.txt .

RUN  pip install --no-cache-dir -r requirements.txt

COPY . /app 

VOLUME [ ":/app" ]

EXPOSE 8888

RUN cd /usr/local/lib/python3.6/site-packages && \
    python /app/extra_lib/setup.py develop

RUN pip install -e extra_lib/

CMD ["/bin/bash"]