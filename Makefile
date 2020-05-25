all:
	@echo "Please invoke one of the following instead: "
	@awk '/^#: / {sub(/#: /, "\t"); print $$0}' $(firstword $(MAKEFILE_LIST))
	@false

#: release - push a new release to GitHub
release: fst_lookup/__version__.py
	version="v$(shell poetry run python3 libexec/print-version.py)" && \
		git commit -a -m "$$version" &&\
		git tag "$$version"
	git push
	git push --tags

#: sync-version - keep package version in sync with pyproject.toml
sync-version: fst_lookup/__version__.py

fst_lookup/__version__.py: pyproject.toml
	poetry run python3 libexec/update-version.py

.PHONY: all release sync-version new-version
