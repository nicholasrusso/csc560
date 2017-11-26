FROM python:3.5
RUN apt-get update && apt-get install gcc build-essential python3-dev php5-pgsql postgresql --assume-yes
ENV PYTHON_35_INCLUDE /usr/include/python3.4m/Python.h
ENV PYTHON_35_LIB /usr/lib/python3.4/config-3.4m-x86_64-linux-gnu
ENV POSTGRES_LIB /usr/lib/postgresql/9.4/lib
RUN mkdir /project
WORKDIR /project
COPY . .
WORKDIR /project/libpg_query-9.5-latest/
RUN make python
RUN service postgresql restart

ENTRYPOINT sleep infinity