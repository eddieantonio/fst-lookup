# Help make a release.
release: fst_lookup/__version__.py
	version="v$(shell poetry run python3 libexec/print-version.py)" \
		git commit "$$version" \
		git tag "$$version"

fst_lookup/__version__.py: pyproject.toml
	poetry run python3 libexec/update-version.py
