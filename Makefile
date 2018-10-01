
init:
	python -m pip install pipenv
	pipenv install --dev

run:
	python engineering_diplomats/main.py

test:
	pipenv run py.test --show-progress --cov=./

reqs:
	pipenv lock -r -d > requirements.txt

docs:
	ifeq ($(PIPENV_ACTIVE),1) 
		echo Beginning documentation build...
		sphinx-apidoc -f -o ./docs/source .
		sphinx-build -b html ./docs/source ./docs/ 
		echo "Documentation build complete."
	else 
		echo Please run 'pipenv shell' first. 

tarball:
	tar -czf credentials.tar.gz token.json .env credentials.json logs
	travis login --github-token $(TRAVIS_TOKEN)
	travis encrypt TOKEN=$(TRAVIS_TOKEN) --add
	gpg -c credentials.tar.gz
	del credentials.tar.gz
