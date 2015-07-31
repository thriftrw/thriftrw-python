.PHONY: test lint docs docsopen clean

test_args := \
	--cov thriftrw \
	--cov-config .coveragerc \
	--cov-report term-missing \
	tests

test:
	PYTHONDONTWRITEBYTECODE=1 py.test $(test_args)

lint:
	flake8 thriftrw tests

docs:
	make -C docs html

docszip: docs
	cd docs/_build/html; zip -r ../html.zip .

docsopen: docs
	open docs/_build/html/index.html

clean:
	rm -rf thriftrw.egg-info
	find tests thriftrw -name \*.pyc -delete
	make -C docs clean
