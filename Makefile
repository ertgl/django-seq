.DEFAULT_GOAL=""


VIRTUALENV_PATH=.venv


API_DOCS_PATH=docs/source/api


venv:
	test -d $(VIRTUALENV_PATH) || virtualenv $(VIRTUALENV_PATH) -p python3


venv.clean:
	rm -rf $(VIRTUALENV_PATH)


deps.install:
	pip install -r requirements/requirements-dev.txt
	pip install -r requirements/requirements.txt
	pip install -r requirements/requirements-docs.txt
	pip install -r requirements/requirements-samples.txt


link:
	pip install -e .


prepare: deps.install link


django.migrations:
	cd dev/django/ && python manage.py makemigrations django_seq --no-header


django.migrate:
	cd dev/django/ && python manage.py migrate


django: django.migrations django.migrate


django.clean:
	cd dev/django && \
		rm -f db.sqlite3


typecheck:
	mypy . --namespace-packages --explicit-package-bases


mypy.clean:
	rm -rf .mypy_cache


test.app: django.clean django.migrations django.migrate
	cd dev/django && \
		python manage.py test django_seq


test.samples.swappable:
	cd samples/swappable && \
		rm -f db.sqlite3 && \
		rm -f sequences/migrations/*.py && \
		touch sequences/migrations/__init__.py && \
		python manage.py makemigrations sequences --no-header && \
		python ../../dev/django/misc/prepare_swappable_migration.py && \
		python manage.py migrate && \
		python manage.py test sequences


test.samples.issues:
	cd samples/issues && \
		rm -f db.sqlite3 && \
		rm -f issues/migrations/*.py && \
		touch issues/migrations/__init__.py && \
		python manage.py makemigrations issues --no-header && \
		python manage.py migrate && \
		python manage.py test issues


test.samples: test.samples.issues test.samples.swappable


.PHONY: test
test: typecheck test.app test.samples


.PHONY: docs
docs:
	mkdir -p $(API_DOCS_PATH)
	sphinx-apidoc django_seq -f -M -o $(API_DOCS_PATH)
	python docs/source/_postprocessors/_run.py
	cd docs && make html


.PHONY: docs.clean
docs.clean:
	cd docs && make clean
	rm -rf $(API_DOCS_PATH)


clean: venv.clean mypy.clean docs.clean django.clean
