FROM minio/minio:latest

VOLUME /data

COPY init.sh /usr/local/bin/init.sh
RUN chmod +x /usr/local/bin/init.sh

EXPOSE 9000
EXPOSE 9001

ENTRYPOINT ["/usr/local/bin/init.sh"]
