# slim-buster needs dependencies for selenium
FROM python:3.9

# Don't buffer logs or write pyc
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set Virtual env as active python environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install all requirements
COPY requirements*.txt /tmp/
RUN pip install --upgrade pip && pip install --no-cache-dir -r /tmp/requirements.dev.txt

# Install Chrome & Chromedriver
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get -yqq update && \
    apt-get -yqq install google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*
RUN seleniumbase install chromedriver latest

# Run as non-root user
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

COPY . .

ENTRYPOINT [ "/bin/bash" ]
CMD [ "entrypoint.sh" ]
