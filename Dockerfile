FROM python:3.7
ADD . /engineeringdiplomats.org
WORKDIR /engineeringdiplomats.org
RUN python -m pip install pipenv
RUN pipenv install --dev
CMD ["python", "engineeringdiplomats.org/__main__.py"]
