FROM python:3.7.1-slim-stretch
LABEL maintainer="Simon Woldemichael <simon.woldemichael@ttu.edu>"
ADD . /engineeringdiplomats.org
WORKDIR /engineeringdiplomats.org
RUN python -m pip install pipenv
RUN pipenv install --dev
RUN pipenv run pip install -e .
CMD ["pipenv", "run", "python", "production/wsgi.py"]
