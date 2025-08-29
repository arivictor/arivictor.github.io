PYTHON=python3

new-post:
	@$(PYTHON) new.py "$(TITLE)"

generate-tags:
	@$(PYTHON) generate_tags.py

build: generate-tags
	bundle exec jekyll build

serve: generate-tags
	bundle exec jekyll serve