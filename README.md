# URL Scan

Powered by [Streamlit](https://docs.streamlit.io/) + [AWS Rekognition](https://docs.aws.amazon.com/rekognition/latest/dg/text-detection.html).
Specifically, Streamlit runs the user interaction and AWS Rekognition does the OCR, and another Python library [URLExtract](https://urlextract.readthedocs.io/en/latest/index.html) does the URL matching.

## Local Run

### Update AWS connection secrets

- Requires AWS Account with access to Rekognition service ([AWS Tutorial](https://docs.aws.amazon.com/rekognition/latest/dg/setting-up.html))
- Copy or Rename `.env.example` as `.env.dev` and fill in AWS Access Key, Secret Key, Region for your Rekognition account

```sh
mv .env.example .env.dev
```

### Run with Docker

Requires [docker-compose](https://docs.docker.com/compose/install/) to be installed (this comes with Docker Desktop).

```sh
docker-compose up
# Open localhost:8501
```

Use `-d` to detach from logs.

Use `--build` on subsequent runs to rebuild dependencies / docker image.

### Lint, Check, Test with Docker

```sh
# Linting 
docker-compose run streamlit-app nox.sh -s lint
# Unit Testing
docker-compose run streamlit-app nox.sh -s test
# Both
docker-compose run streamlit-app nox.sh
# As needed:
docker-compose build

# E2E Testing
docker-compose up -d --build
# Replace screenshots
docker-compose exec streamlit-app nox -s test -- -m e2e --visual-baseline
# Compare to visual baseline screenshots
docker-compose exec streamlit-app nox -s test -- -m e2e
# Turn off / tear down
docker-compose down
```

### Local Python environment

For code completion / linting / developing / etc.

```sh
python -m venv venv
. ./venv/bin/activate
# .\venv\Scripts\activate for Windows
python -m pip install -r ./src/requirements.dev.txt
pre-commit install

# Linting / Static Checking / Unit Testing
python -m black src
python -m isort --profile=black src
python -m flake8 --config=./src/.flake8 src
```

## Features

- Containerization with [Docker](https://docs.docker.com/)
- Dependency installation with Pip
- Test automation with [Nox](https://nox.thea.codes/en/stable/index.html)
- Linting with [pre-commit](https://pre-commit.com/) and [Flake8](https://flake8.pycqa.org/en/latest/)
- Code formatting with [Black](https://black.readthedocs.io/en/stable/)
- Testing with [pytest](https://docs.pytest.org/en/6.2.x/getting-started.html)
- Code coverage with [Coverage.py](https://coverage.readthedocs.io/en/6.2/)


## Rekognition Limitations

This version sends binary image data to AWS Rekognition, which is limited to 5mb.
To account for this, image uploads that are larger than this size are resized down before sending to AWS.

Rekognition's text detection is limited to 100 words.
Images with more than this limit may benefit from [AWS Textract](https://aws.amazon.com/textract/)


## Next Steps / Ideas

- [ ] makefile
- [x] 5 mb limit without S3 version
- [ ] Option for Textract OCR backend
- [ ] 5 mb limit with S3 version (X from env / config)
- [ ] X mb limit from env / config
- [ ] FastAPI backend
- [ ] API_key access to backend without streamlit
- [ ] Option for Tesseract / non-aws OCR backend
