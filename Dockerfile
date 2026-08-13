FROM nikolaik/python-nodejs:python3.10-nodejs20

Install system dependencies

RUN apt-get update && apt-get install -y --no-install-recommends \
curl \
xz-utils \
&& rm -rf /var/lib/apt/lists/*

Download and install static FFmpeg (John Van Sickle build)

RUN curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz \
-o ffmpeg.tar.xz && \
tar -xJf ffmpeg.tar.xz && \
mv ffmpeg--static/ffmpeg /usr/local/bin/ && \
mv ffmpeg--static/ffprobe /usr/local/bin/ && \
rm -rf ffmpeg*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["bash", "start"]
