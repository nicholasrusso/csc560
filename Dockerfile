FROM python:3.5
RUN apt-get update && apt-get install gcc build-essential python3-dev php5-pgsql postgresql vim --assume-yes
ENV PYTHON_35_INCLUDE /usr/include/python3.4m/Python.h
ENV PYTHON_35_LIB /usr/lib/python3.4/config-3.4m-x86_64-linux-gnu
ENV POSTGRES_LIB /usr/lib/postgresql/9.4/lib
RUN mkdir /project
WORKDIR /project
COPY . .
RUN pip3 install -r requirements.txt
WORKDIR /project/libpg_query-9.5-latest/
RUN make python
WORKDIR /project

ENTRYPOINT sleep infinity
