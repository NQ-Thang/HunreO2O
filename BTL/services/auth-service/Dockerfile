FROM alpine:latest

RUN apk add --no-cache php php-cli php-json php-mbstring php-curl

WORKDIR /var/www

COPY . .

EXPOSE 8001

CMD ["php", "-S", "0.0.0.0:8001", "-t", "public"]
