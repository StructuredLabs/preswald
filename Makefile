.PHONY: release update-version build-frontend build-wheel build-docker test-iris cleanup-push test-whl test-local test-gcp upload-to-gcs upload-to-pypi

# todo: add test-gcp
pre-release: update-version build-frontend build-wheel build-docker test-iris test-whl test-local upload-to-gcs 

release: pre-release cleanup-push upload-to-pypi

update-version:
	@echo "Updating preswald version..."
	@current_version=$$(grep "version" pyproject.toml | grep -v "^#" | head -1 | sed -E 's/.*version = "([^"]+)".*/\1/'); \
	if [ -z "$$current_version" ]; then \
		echo "Error: Could not find version in pyproject.toml"; \
		exit 1; \
	fi; \
	major=$$(echo $$current_version | cut -d. -f1); \
	minor=$$(echo $$current_version | cut -d. -f2); \
	patch=$$(echo $$current_version | cut -d. -f3); \
	new_patch=$$(echo "$$patch + 1" | bc); \
	new_version="$$major.$$minor.$$new_patch"; \
	if [ "$$(uname)" = "Darwin" ]; then \
		sed -i '' "s/version = \"$$current_version\"/version = \"$$new_version\"/" pyproject.toml; \
	else \
		sed -i "s/version = \"$$current_version\"/version = \"$$new_version\"/" pyproject.toml; \
	fi; \
	echo "Version updated from $$current_version to $$new_version"

build-frontend:
	@echo "Building frontend..."
	python -m preswald.build frontend

build-wheel:
	@echo "Building wheel..."
	python -m build
	@echo "Wheel built successfully"

build-docker:
	@echo "Building preswald docker image..."
	@mkdir -p docker/tmp
	@latest_wheel=$$(ls -t dist/preswald-*.whl | head -1); \
	wheel_exists=false; \
	if [ -f "$$latest_wheel" ]; then \
		cp $$latest_wheel docker/wheel.whl; \
		wheel_exists=true; \
	fi;
	@echo "wheel_exists=$$wheel_exists"
	cd docker && docker buildx build --platform linux/amd64 --pull=false --no-cache \
		--build-arg USE_LOCAL_WHEEL=$$wheel_exists \
		-t preswald -f preswald.Dockerfile .
	docker tag preswald structuredlabs/preswald-base

test-iris:
	@echo "Testing iris example app..."
	docker build --pull=false --no-cache -t iris_app -f ./docker/test/iris_app.Dockerfile .
	@echo "Running automated test of iris app..."
	docker run -d -p 8501:8501 --name iris_test_container iris_app
	@echo "Waiting for app to start..."
	sleep 10
	@echo "Testing app endpoint..."
	curl -s --fail http://localhost:8501 || (docker stop iris_test_container && docker rm iris_test_container && echo "Test failed: could not connect to app" && exit 1)
	@echo "Test successful, cleaning up container..."
	docker stop iris_test_container
	docker rm iris_test_container

cleanup-push:
	@echo "Pushing to DockerHub..."
	@echo "Authenticating with DockerHub..."
	@echo "$$DOCKERHUB_TOKEN" | docker login -u "$$DOCKERHUB_USERNAME" --password-stdin
	docker push structuredlabs/preswald-base
	@echo "Cleaning up..."
	@rm -f docker/wheel.whl
	docker logout

test-whl:
	@echo "Testing preswald wheel..."
	@latest_wheel=$$(ls -t dist/preswald-*.whl | head -1); \
	conda create -n preswald_test python=3.12 -y; \
	conda activate preswald_test; \
	pip install $$latest_wheel; \
	preswald --version; \
	conda deactivate; \
	conda env remove -n preswald_test -y

test-local:
	@echo "Running local deployment test..."
	./autotest/deployments/local/test.sh

test-gcp:
	@echo "Running GCP deployment test..."
	./autotest/deployments/gcp/test.sh

upload-to-gcs:
	@echo "Uploading wheel to Google Cloud Storage..."
	@if [ -z "$$PRESWALD_DEPLOYER_DEV_SA" ]; then \
		echo "Error: PRESWALD_DEPLOYER_DEV_SA environment variable not set"; \
		exit 1; \
	fi; \
	if ! command -v gcloud >/dev/null 2>&1; then \
		echo "Error: gcloud command not found."; \
		exit 1; \
	fi; \
	if ! command -v gsutil >/dev/null 2>&1; then \
		echo "Error: gsutil command not found."; \
		exit 1; \
	fi; \
	latest_wheel=$$(ls -t dist/preswald-*.whl | head -1); \
	if [ ! -f "$$latest_wheel" ]; then \
		echo "Error: No wheel file found in dist/ directory."; \
		exit 1; \
	fi; \
	wheel_filename=$$(basename $$latest_wheel); \
	echo "$$PRESWALD_DEPLOYER_DEV_SA" | base64 --decode > /tmp/service-account.json; \
	gcloud auth activate-service-account --key-file=/tmp/service-account.json || { echo "Failed to authenticate with Google Cloud"; rm -f /tmp/service-account.json; exit 1; }; \
	gsutil cp $$latest_wheel gs://preswald_wheels/$$wheel_filename || { echo "Failed to upload to Google Cloud Storage"; rm -f /tmp/service-account.json; exit 1; }; \
	rm -f /tmp/service-account.json; \
	echo "Successfully uploaded $$wheel_filename to gs://preswald_wheels/"

upload-to-pypi:
	@echo "Uploading wheel to PyPI..."
	@if ! command -v twine >/dev/null 2>&1; then \
		echo "Error: twine command not found. Install with: pip install twine"; \
		exit 1; \
	fi; \
	if [ -z "$$PYPI_API_TOKEN" ]; then \
		echo "Error: PYPI_API_TOKEN environment variable not set"; \
		exit 1; \
	fi; \
	latest_wheel=$$(ls -t dist/preswald-*.whl | head -1); \
	if [ ! -f "$$latest_wheel" ]; then \
		echo "Error: No wheel file found in dist/ directory."; \
		exit 1; \
	fi; \
	echo "Uploading $$(basename $$latest_wheel) to PyPI..."; \
	TWINE_USERNAME=__token__ TWINE_PASSWORD=$$PYPI_API_TOKEN twine upload "$$latest_wheel" || { \
		echo "Failed to upload to PyPI"; \
		exit 1; \
	}; \
	echo "Successfully uploaded $$(basename $$latest_wheel) to PyPI"

