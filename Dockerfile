# Use a base image with a Linux distribution, for example, Ubuntu
FROM ubuntu:latest

# Install Python and CMake
RUN apt-get update && \
    apt-get install -y python3 python3-pip cmake

# Install stuff needed for perf (unsupported instuction count mac however)
RUN apt-get -y install linux-tools-common linux-base 
RUN apt -y install linux-tools-generic

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the Bash script into the container
COPY . .

# Make port 80 available to the world outside this container
EXPOSE 80

# Command to run when the container starts
CMD ["bash", "experiments/run.sh"]
