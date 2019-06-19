FROM python:alpine

WORKDIR /app

COPY --chown=65534:65534 Pipfile Pipfile.lock /app/ 

RUN apk add --update --no-cache gcc libc-dev linux-headers
RUN pip3 install pipenv
RUN pipenv install --system --deploy

COPY --chown=65534:65534 . /app/
# RUN chmod -R 755 /app
USER 65534:65534

ENTRYPOINT  [ "python3", "/app/cloudbot/__main__.py" ]