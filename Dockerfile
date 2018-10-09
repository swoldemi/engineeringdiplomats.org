FROM python:3.7
MAINTAINER Simon "simon.woldemichael@ttu.edu"
ADD . /engineeringdiplomats.org
WORKDIR /engineeringdiplomats.org
RUN python -m pip install pipenv
RUN pipenv install --dev
RUN pipenv run pip install -e .
EXPOSE 80
CMD ["pipenv", "run", "python", "production/wsgi.py"]
