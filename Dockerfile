FROM python:2.7
ADD . app
WORKDIR app
RUN pip install -e .
RUN make
CMD make serve
EXPOSE 8000
