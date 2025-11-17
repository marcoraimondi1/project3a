FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN apt-get update && \
	apt-get install -y --no-install-recommends \
		build-essential \
		libxml2-dev \
		libxslt1-dev \
		zlib1g-dev \
		gcc && \
	rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app.py"]