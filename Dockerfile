FROM nikolaik/python-nodejs:python3.10-nodejs20

# Install system dependencies & FFmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

# Download and install static FFmpeg
RUN curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz \
    -o ffmpeg.tar.xz && \
    tar -xJf ffmpeg.tar.xz && \
    mv ffmpeg-*-static/ffmpeg /usr/local/bin/ && \
    mv ffmpeg-*-static/ffprobe /usr/local/bin/ && \
    rm -rf ffmpeg*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Fix: Make sure 'ffmpeg' word is removed from your requirements.txt before running this
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

CMD ["bash", "start"]
