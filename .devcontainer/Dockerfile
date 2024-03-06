FROM mcr.microsoft.com/devcontainers/cpp:0-ubuntu-22.04

RUN apt-get update \
        && export DEBIAN_FRONTEND=noninteractive \
        && apt-get -y install --no-install-recommends clang-format openmpi-bin libopenmpi-dev gnuplot git-lfs \
        && apt-get autoremove -y \
        && apt-get clean -y \
        && rm -rf /var/lib/apt/lists/*


RUN wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py \
    && pip install --upgrade pip \
    && pip install numpy gcovr

# Customise my zhs taken from: https://github.com/deluan/zsh-in-docker
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.1.5/zsh-in-docker.sh)" -- \
    # -p https://github.com/zsh-users/zsh-autosuggestions \
    # -p https://github.com/zsh-users/zsh-completions \
    -p https://github.com/zsh-users/zsh-history-substring-search \
    -p https://github.com/zsh-users/zsh-syntax-highlighting \
    -p 'history-substring-search' \
    -a 'bindkey "\$terminfo[kcuu1]" history-substring-search-up' \
    -a 'bindkey "\$terminfo[kcud1]" history-substring-search-down'

# Override the configuration files
RUN git clone https://github.com/damienbose/dotfile.git \
    && mv dotfile/.p10k.zsh ~ \
    && mv dotfile/.zshrc ~ \
    && rm -rf dotfile


ENTRYPOINT [ "/bin/zsh" ]