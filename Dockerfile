FROM ubuntu:22.04
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

# Basic utility packages
RUN sed -i 's@http://archive.ubuntu.com/@http://mirrors.tuna.tsinghua.edu.cn/@g' /etc/apt/sources.list && \
    sed -i 's@http://security.ubuntu.com/@http://mirrors.tuna.tsinghua.edu.cn/@g' /etc/apt/sources.list && \
    apt clean &&\
    apt update &&\
    apt install -y sudo bash git cmake vim tar openssh-server rsync python3.10 python3-pip gnupg curl

# Install MongoDB
RUN curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | \
    gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg \
    --dearmor &&\
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/8.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-8.0.list
# This step takes a long time because of the large size of the MongoDB package
RUN apt update &&\
    apt install -y mongodb-org

EXPOSE 27017

# add user and initialize mongodb
RUN mkdir -p /data/db /var/log/mongodb &&\
    chown -R mongodb:mongodb /data/db /var/log/mongodb &&\
    useradd -ms /bin/bash -G sudo user &&\
    passwd -d user

COPY docker/mongod.conf /etc/mongod.conf

VOLUME /home/user/bookstore
USER user
WORKDIR /home/user
CMD ["/bin/bash"]
