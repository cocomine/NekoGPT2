FROM python:latest
LABEL authors="cocomine"
LABEL version="0.1.5"
WORKDIR /bot

ENV DISCORD_TOKEN (Your Discord token)
ENV CHATGPT_TOKEN (Your ChatGPT access token)
ENV MYSQL_HOST (Your SQL host)
ENV MYSQL_USER (Your SQL username)
ENV MYSQL_PASSWORD (Your SQL password)
ENV MYSQL_DATABASE (Your SQL database)
ENV BOT_NAME (Your Bot Name)
ENV SPEECH_KEY (Your Speech key)
ENV SPEECH_REGION (Your Speech region)

# Add file
ADD src/ ./

# set-up command
RUN apt-get --yes update; apt-get --yes upgrade;
RUN apt --yes install libgstreamer1.0-0
RUN apt --yes install gstreamer1.0-plugins-base
RUN apt --yes install gstreamer1.0-plugins-good
RUN apt --yes install gstreamer1.0-plugins-bad
RUN apt --yes install gstreamer1.0-plugins-ugly
RUN pip install -r requirements.txt

# start-up command
ENTRYPOINT ["python", "main.py"]

