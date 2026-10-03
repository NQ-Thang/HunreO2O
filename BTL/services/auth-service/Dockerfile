FROM alpine:3.20

# Cài đặt PHP runtime và các extension tối ưu hóa hiệu năng
RUN apk add --no-cache \
    php83 \
    php83-cli \
    php83-json \
    php83-mbstring \
    php83-curl \
    php83-openssl \
    php83-pdo \
    php83-pdo_mysql \
    php83-opcache \
    curl \
    && ln -sf /usr/bin/php83 /usr/bin/php

# Cấu hình OPcache tăng tốc thực thi PHP Microservice
RUN echo "opcache.enable_cli=1" >> /etc/php83/conf.d/00_opcache.ini && \
    echo "opcache.memory_consumption=128" >> /etc/php83/conf.d/00_opcache.ini && \
    echo "opcache.interned_strings_buffer=8" >> /etc/php83/conf.d/00_opcache.ini && \
    echo "opcache.max_accelerated_files=10000" >> /etc/php83/conf.d/00_opcache.ini && \
    echo "opcache.validate_timestamps=0" >> /etc/php83/conf.d/00_opcache.ini

WORKDIR /var/www

COPY . .

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

CMD ["php", "-S", "0.0.0.0:8001", "-t", "public"]
