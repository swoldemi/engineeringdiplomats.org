FROM python:3.6.6-alpine
ADD . /engineeringdiplomats.org
WORKDIR /engineeringdiplomats.org
RUN python -m pip install pipenv
RUN pipenv install --dev
CMD ["python", "engineeringdiplomats.org/__main__.py"]
