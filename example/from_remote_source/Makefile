.PHONY: create-build-image

create-build-image:
	ITERATION=0 docker-rpm-builder genspec tmux.spectemplate build-image/tmux.spec
	cd build-image ; docker build -t tmux-drbbuild .
