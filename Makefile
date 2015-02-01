.PHONY: srpm clean distclean pypirelease test fulltest pypirelease

devenv: setup.py
	test -r devenv || virtualenv-2.7 devenv
	devenv/bin/pip install --editable . --upgrade
	devenv/bin/pip install wheel
	devenv/bin/pip install bpython


rpm: tmp 	
ifndef BUILD_IMAGE
	@echo "Must pass BUILD_IMAGE
	@exit 1
endif
	VERSION_NUMBER=$(shell python setup.py --version) docker-rpm-builder dir ${BUILD_IMAGE} .

test: devenv
	devenv/bin/python -m unittest2 discover -v

fulltest: test
	. devenv/bin/activate && cd drb/integration_tests && ./test.sh ${TEST_IMAGES}

tmp:
	mkdir -p tmp

clean:
	rm -rf tmp build dist 

distclean: clean
	rm -rf prodenv devenv *.tar.gz docker-rpm-builder.spec

stablerelease:
ifndef RELEASE_NUMBER
	@echo "Must pass RELEASE_NUMBER"
	@exit 1
endif
	# always recreate
	rm -rf prodenv
	virtualenv-2.7 prodenv
	sed -i -e "s/\dev0//g" version.txt
	[ "${RELEASE_NUMBER}" == $(cat version.txt) ] || { echo "Release number version mismatch"; exit 1; }
	prodenv/bin/pip install .
	prodenv/bin/pip freeze > requirements.txt
	prodenv/bin/pip install wheel
	prodenv/bin/python setup.py bdist_wheel sdist
	git checkout -- version.txt
	rm -rf *.egg-info

pypirelease:
ifndef BUILD_NUMBER
	@echo "Must pass BUILD_NUMBER for upload"
	@exit 1
endif
	# always recreate
	rm -rf prodenv
	virtualenv-2.7 prodenv
	echo "${BUILD_NUMBER}" >> version.txt
	prodenv/bin/pip install .
	prodenv/bin/pip freeze > requirements.txt
	prodenv/bin/pip install wheel
	prodenv/bin/python setup.py bdist_wheel sdist 
	git checkout -- version.txt
	rm -rf *.egg-info
