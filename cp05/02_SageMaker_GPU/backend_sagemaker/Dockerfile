FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04

RUN apt-get update
ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get install -yq --no-install-recommends python3-pip \
        python3-dev \
        wget \
        git  \
        tzdata && apt-get upgrade -y && apt-get clean

RUN ln -s /usr/bin/python3 /usr/bin/python

COPY requirements.txt .
RUN pip install -U pip &&\
  pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

COPY ./src .
ENTRYPOINT [ "python", "app.py"]
