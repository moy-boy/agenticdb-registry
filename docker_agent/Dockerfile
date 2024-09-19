FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

EXPOSE 8001

COPY ./main.py /code/


CMD ["fastapi", "run", "main.py", "--port", "8001"]