FROM python:3.13-bookworm

RUN apt-get update && \
    apt-get dist-upgrade -y

COPY dist/*.whl /tmp/uedition-editor-source/

RUN pip install /tmp/uedition-editor-source/*.whl

CMD [ "uvicorn", "--port", "8000", "--host", "0.0.0.0", "uedition_editor:app" ]
