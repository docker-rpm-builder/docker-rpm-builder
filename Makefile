.PHONY: srpm clean

#srpm: export BUILD_NUMBER=$(shell git log --pretty=oneline | wc -l)
#srpm: export GIT_REVISION=$(shell git rev-parse HEAD)
srpm: tmp 	
	[ -z "$(shell git status --porcelain)" ]
	git archive $(shell git rev-parse --abbrev-ref HEAD) -o tmp/docker-rpm-builder.tar.gz
	perl -p -i -e 's/\$$\{([^}]+)\}/defined $$ENV{$$1} ? $$ENV{$$1} : $$&/eg' < docker-rpm-builder.spectemplate > tmp/docker-rpm-builder.spec
	rpmbuild --define '_sourcedir ./tmp'  --define '_srcrpmdir ./tmp' -bs tmp/docker-rpm-builder.spec


tmp:
	mkdir -p tmp

clean:
	rm -rf tmp build dist

