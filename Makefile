
init:
	python -m pip install pipenv
	pipenv install --dev

run:
	pipenv run python engineering_diplomats/main.py

test:
	pipenv run py.test -s --show-progress --cov=./

docs:
	ifeq ($(PIPENV_ACTIVE),1) 
		echo Beginning documentation build...
		sphinx-apidoc -f -o ./docs/engineering_diplomats .
		sphinx-build -b html ./docs/engineering_diplomats ./docs/ 
		echo "Documentation build complete."
	else 
		echo Please run 'pipenv shell' first. 

tarball:
	tar -czf credentials.tar.gz token.json .env credentials.json gcp-creds.json
	travis login --github-token $(TRAVIS_TOKEN)
	travis encrypt TOKEN=$(TRAVIS_TOKEN) --add
	gpg -c credentials.tar.gz
	rm credentials.tar.gz
