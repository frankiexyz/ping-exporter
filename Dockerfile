FROM alpine:latest

RUN apk update && apk add python3 py-pip fping
COPY ./ping-exporter.py /
EXPOSE 8085
CMD ["python3", "/ping-exporter.py"]
