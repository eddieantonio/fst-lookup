# Help make a release.
release: fst_lookup/__version__.py
	git tag v$(shell poetry run python3 libexec/print-version.py)

fst_lookup/__version__.py: pyproject.toml
	poetry run python3 libexec/update-version.py
