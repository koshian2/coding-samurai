FROM ubuntu:22.04

RUN apt-get update
ENV TZ=Asia/Tokyo
ENV LANG=en_US.UTF-8
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get install -yq --no-install-recommends python3-pip \
        python3-dev \
        git \
        wget \
        vim \
        tzdata && apt-get upgrade -y && apt-get clean

RUN ln -s /usr/bin/python3 /usr/bin/python

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080

COPY /src .
CMD ["python", "app.py"]