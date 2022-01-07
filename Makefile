#
PACKAGE_DIR = ""
REF_PLUGINS_PATH = ""

create:
	@echo
	@echo "-----------------------------------"
	@echo "Create OSGeo4W archive."
	@echo "-----------------------------------"
	@scripts/make.sh $(REF_PLUGINS_PATH)

deploy: create
	@echo
	@echo "-----------------------------------"
	@echo "Deploy OSGeo4W archive."
	@echo "-----------------------------------"
	@scripts/deploy.sh $(PACKAGE_DIR)
