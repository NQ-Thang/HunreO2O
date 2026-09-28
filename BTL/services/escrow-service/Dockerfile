FROM alpine:latest

RUN apk add --no-cache php php-cli php-json php-mbstring php-curl

WORKDIR /var/www

COPY . .

EXPOSE 8003

CMD ["php", "-S", "0.0.0.0:8003", "-t", "public"]
