[![Updates](https://pyup.io/repos/github/swoldemi/engineeringdiplomats.org/shield.svg)](https://pyup.io/repos/github/swoldemi/engineeringdiplomats.org/)
[![Coverage Status](https://coveralls.io/repos/github/swoldemi/engineeringdiplomats.org/badge.svg)](https://coveralls.io/github/swoldemi/engineeringdiplomats.org)
## [engineeringdiplomats.org](http://engineeringdiplomats.org)

A web application for Texas Tech University's Engineering Diplomats.

## Progress
   - Trello Board: https://trello.com/b/Hr7bwsio/engineeringdiplomatsorg


## Local Setup
Note: The `backpop` directory and master `.env` file are gitignored.
1. [Install Python 3.7](https://www.python.org/downloads/release/python-370/)
2. [Install Docker](https://www.docker.com/get-started)
3. Install `make`
    - Windows ([Chocolatey](https://chocolatey.org/docs/installation)): `choco install make`
    - Mac ([Homebrew](http://brewformulas.org/Make)): `brew install make`
3. Begin development environment
    1. `git clone https://github.com/swoldemi/engineeringdiplomats.org`
    2. `cd engineeringdiplomats.org`
    3. `make init`
    4. `docker-compose up -d`
    5. `python backpop/init_db.py`
    6. `make start`
4. Go to `localhost:8080` in your browser


## What this is
1. Displays International Engineering Program and Engineering Diplomats' events for view by anyone.
2. A centralized place for anyone to ask questions related to the Whitacre College of Engineering's International Engineering Requirement.
3. Allows only current Engineering Diplomats and TTU Study Abroad advisors to answer student ping questions.
4. Provides quick access to a variety of Study Abroad related resources for students of the Whitacre College of Engineering.
5. Provides a custom way for current Engineering Diplomats to sign up for point related events.
6. Hosts resources which assist Engineering Diplomats during their office hours.

## What this is not 
1. A replacement for http://www.depts.ttu.edu/coe/iep/
2. A replacement for http://www.depts.ttu.edu/coe/iep/diplomats.php