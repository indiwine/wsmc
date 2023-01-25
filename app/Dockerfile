FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update &&  \
    apt-get -y upgrade &&  \
    apt-get install -y locales-all make git zlib1g-dev libssl-dev gperf cmake g++

RUN cd /tmp/ && \
    git clone https://github.com/tdlib/td.git && \
    cd td && \
    rm -rf build &&  \
    mkdir build &&  \
    cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX:PATH=../tdlib .. && \
    cmake --build . --target install && \
    rm -rf /tmp/td


WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt && \
    pip cache remove * && \
    pip cache purge
COPY . /app/

CMD python manage.py runserver 0.0.0.0:8000

