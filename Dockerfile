FROM python:3.7.9-buster

ARG DEBIAN_FRONTEND=noninteractive
ARG UID
ARG GID

COPY requirements.txt /tmp
RUN pip3 install --no-cache-dir -U pip &&\
    pip3 install --no-cache-dir -U -r /tmp/requirements.txt &&\
    rm /tmp/requirements.txt

RUN groupadd -g ${GID} gawai &&\
    useradd -ms /bin/bash -u ${UID} -g gawai gawai

USER gawai

EXPOSE 3080 6379-6382 8265 10000-10999

ENTRYPOINT [ "bash" ]