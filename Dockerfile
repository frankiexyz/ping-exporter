FROM alpine:latest

RUN apk update && apk add python2 py-pip fping
COPY ./ping-exporter.py /
EXPOSE 8085
CMD ["python2", "/ping-exporter.py"]
