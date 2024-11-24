FROM python:3.10.11-slim-bullseye
LABEL authors="cocomine"
LABEL version="2.0.0"
WORKDIR /bot

ENV PYTHON_ENV production
ENV DISCORD_TOKEN (Your Discord token)
ENV BOT_NAME (Your Bot Name)
ENV SPEECH_KEY (Your Speech key)
ENV SPEECH_REGION (Your Speech region)
ENV OPENAI_BASE_URL default
ENV OPENAI_API_KEY (Your Openai api key)
ENV OPENAI_ASSISTANT_ID ""
ENV SQL_DRIVER sqlite3
ENV MYSQL_HOST ""
ENV MYSQL_PORT ""
ENV MYSQL_USER ""
ENV MYSQL_PASSWORD ""
ENV MYSQL_DATABASE ""
ENV DISCORD_CUSTOM_LOADING_EMOJI ""

# set-up command
RUN apt-get --yes update; apt-get --yes upgrade;
RUN apt --yes install libgstreamer1.0-0
RUN apt --yes install gstreamer1.0-plugins-base
RUN apt --yes install gstreamer1.0-plugins-good
RUN apt --yes install gstreamer1.0-plugins-bad
RUN apt --yes install gstreamer1.0-plugins-ugly
RUN apt --yes install ffmpeg

# Install build tools
RUN apt --yes install wget
RUN apt --yes install build-essential

# Install openssl 3.4.0
RUN wget -O - https://github.com/openssl/openssl/releases/download/openssl-3.4.0/openssl-3.4.0.tar.gz | tar zxf -
RUN ./openssl-3.4.0/config --prefix=/usr/local
RUN make -j $(nproc)
RUN make install_sw install_ssldirs
RUN ldconfig -v
ENV SSL_CERT_DIR /etc/ssl/certs

# Uninstall build tools
RUN apt --yes remove wget
RUN apt --yes remove build-essential

# Add requirements
RUN mkdir "../database"
ADD requirements.txt ./
RUN pip install -r requirements.txt

# Add file
ADD src/ ./

# Add volume
VOLUME ["/database"]

# start-up command
ENTRYPOINT ["python", "main.py"]

