PYTHON=python3

new-post:
	@$(PYTHON) tools/create_post.py "$(TITLE)"

generate-tags:
	@$(PYTHON) tools/generate_tags.py

build: generate-tags
	bundle exec jekyll build

serve: generate-tags
	bundle exec jekyll serve