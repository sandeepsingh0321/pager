# To stop Dockter generating this file and start editing it yourself,
# rename it to "Dockerfile".

# This tells Docker which base image to use.
FROM python:3.7-alpine

WORKDIR /app/

# This section copies your project's files into the image
COPY bin/process_log.py /app/
ENV PATH /app/:$PATH

# This sets the default user when the container is run
USER root

# This tells Docker the default command to run when the container is started
ENTRYPOINT ["python3", "/app/process_log.py"]
