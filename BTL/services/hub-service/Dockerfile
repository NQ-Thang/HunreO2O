FROM alpine:latest

RUN apk add --no-cache php php-cli php-json php-mbstring php-curl

WORKDIR /var/www

COPY . .

EXPOSE 8004

CMD ["php", "-S", "0.0.0.0:8004", "-t", "public"]
