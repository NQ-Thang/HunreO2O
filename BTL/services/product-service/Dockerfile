FROM alpine:latest

RUN apk add --no-cache php php-cli php-json php-mbstring php-curl

WORKDIR /var/www

COPY . .

EXPOSE 8002

CMD ["php", "-S", "0.0.0.0:8002", "-t", "public"]
