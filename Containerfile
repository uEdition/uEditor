FROM python:3.13-bookworm

RUN useradd -u 1000 -g 100 -d /etc/ueditor -m ueditor

RUN apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get install -y tini

COPY dist/*.whl /tmp/uedition-editor-source/

RUN pip install /tmp/uedition-editor-source/*.whl

USER ueditor

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD [ "uvicorn", "--port", "8000", "--host", "0.0.0.0", "uedition_editor:app" ]
