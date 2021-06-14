
FROM python:3.7-slim-buster

RUN useradd --user-group --create-home --no-log-init --shell /bin/bash user 

WORKDIR /home/user/app

ENV PYTHONPATH=/home/user/app

RUN echo "deb http://security.debian.org jessie/updates main" | tee -a /etc/apt/sources.list

RUN apt-get update &&\
    apt-get -y upgrade &&\
    apt-get -y install gcc git vim&&\
    apt-get -y install wget&&\
    apt-get -y install libglib2.0-0&&\
    apt-get -y install libsm6 libxext6 &&\
    apt-get -y install libxrender-dev &&\
    apt-get -y install libhdf5-dev &&\ 
    apt-get -y install libopenexr-dev &&\ 
    apt-get -y install libavcodec-dev &&\
    apt-get -y install libavformat-dev &&\
    apt-get -y install libswscale-dev &&\
    apt-get -y install libgtk-3-dev &&\
    apt-get -y install libjasper-dev &&\
    apt-get -y install libqtgui4 &&\
    apt install libqt4-test &&\ 
    apt-get -y install zip &&\
    apt-get -y install libffi6 &&\ 
    apt-get -y install libffi-dev &&\
    apt-get -y install virtualenv python3-virtualenv &&\
    apt-get -y install libatlas-base-dev libfreetype6-dev libjpeg-dev libopenjp2-7-dev libtiff-dev libzmq3-dev pkg-config &&\
    apt -y autoremove

RUN echo "[global]\n extra-index-url=https://www.piwheels.org/simple" > /etc/pip.conf

RUN virtualenv -p /usr/bin/python3 env-dev

RUN chmod +x ./env-dev/bin/activate 

RUN chown -R user:user /usr/local/bin

RUN chmod -R 777 /usr/local/lib/python3.7/site-packages

RUN chown -R user:user /home/user 

RUN echo "export LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1" | tee -a /home/user/.bashrc

RUN echo "export PATH=$PATH:~/.local/bin" | tee -a /home/user/.bashrc 

USER user

RUN ./env-dev/bin/activate

COPY requirements.txt .


RUN  pip3 install --no-cache-dir -r requirements.txt --user

COPY --chown=user . /home/user/app 

RUN cd /usr/local/lib/python3.7/site-packages && \
    /home/user/app/env-dev/bin/python3 /home/user/app/extra_lib/setup.py develop --user

RUN pip install --user extra_lib/  

CMD ["/bin/bash"]
