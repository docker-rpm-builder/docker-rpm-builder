.PHONY: srpm clean distclean pypirelease test

devenv: setup.py
	test -r devenv || virtualenv-2.7 devenv
	devenv/bin/pip install --editable  .
	devenv/bin/pip install wheel
	devenv/bin/pip install bpython


rpm: tmp 	
ifndef BUILD_IMAGE
	@echo "Must pass BUILD_IMAGE
	@exit 1
endif
	VERSION_NUMBER=$(shell python setup.py --version) docker-rpm-builder dir ${BUILD_IMAGE} .

test: devenv
	devenv/bin/python -m unittest discover -v
	. devenv/bin/activate && cd integration_tests && ./test.sh

tmp:
	mkdir -p tmp

clean:
	rm -rf tmp build dist 

distclean: clean
	rm -rf devenv


pypirelease: devenv
ifndef BUILD_NUMBER
	@echo "Must pass BUILD_NUMBER for upload"
	@exit 1
endif
	devenv/bin/python setup.py egg_info --tag-build ${BUILD_NUMBER} bdist_wheel sdist register upload
	# AFTER the build we must 'cleanup' the tag-build info otherwise things stop working. F**K python packaging.
	devenv/bin/python setup.py egg_info

