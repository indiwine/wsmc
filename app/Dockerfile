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


RUN apt-get -y install binutils libproj-dev gdal-bin

WORKDIR /app
COPY requirements.txt /app/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt


COPY social_media/ai/model_files/ /app/social_media/ai/model_files/

COPY . /app/

CMD python manage.py runserver 0.0.0.0:8000

