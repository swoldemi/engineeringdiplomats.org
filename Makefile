
init:
	python -m pip install pipenv
	pipenv install --dev

run:
	python engineering_diplomats/main.py

test:
	pipenv run py.test --show-progress --cov=./

update_reqs:
	pipenv lock -r > requirements.txt

make_docs:
	ifeq ($(PIPENV_ACTIVE),1) 
		echo Beginning documentation build...
		sphinx-apidoc -f -o ./docs/source .
		sphinx-build -b html ./docs/source ./docs/ 
		echo "Documentation build complete."
	else 
		echo Please run 'pipenv shell' first. 
