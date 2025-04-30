# https://docs.docker.com/engine/reference/builder/

FROM python:3.10
COPY dist/*.whl .
RUN pip install ./*.whl
CMD ["ml-rnd-mcp", "--help"]
