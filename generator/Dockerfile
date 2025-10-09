FROM maven:3.9.4-eclipse-temurin-21 AS build-base
WORKDIR /workspace

RUN apt-get update \
	&& apt-get install -y --no-install-recommends git python3 python3-pip curl gnupg2 ca-certificates \
	&& curl -s https://dl.k6.io/key.gpg | apt-key add - \
	&& echo "deb https://dl.k6.io/deb stable main" | tee /etc/apt/sources.list.d/k6.list \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends k6 \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY generator.py .
RUN pip3 install fastapi uvicorn pyyaml requests

# install ssh client so the container can push via git+ssh if an SSH key is provided at runtime
RUN apt-get update \
	&& apt-get install -y --no-install-recommends openssh-client \
	&& rm -rf /var/lib/apt/lists/*

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

CMD ["uvicorn", "generator:app", "--host", "0.0.0.0", "--port", "5000"]
