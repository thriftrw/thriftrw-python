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
	PYTHONDONTWRITEBYTECODE=1 make -C docs html

docszip: docs
	cd docs/_build/html; zip -r ../html.zip .

docsopen: docs
	open docs/_build/html/index.html

clean:
	rm -rf thriftrw.egg-info
	rm -rf dist
	rm -rf build
	find tests thriftrw -name \*.pyc -delete
	find tests thriftrw -name \*.c -delete
	find tests thriftrw -name \*.so -delete
	make -C docs clean
