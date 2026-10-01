<?php
$caPath = getenv('MYSQL_ATTR_SSL_CA');
if (!$caPath || !file_exists($caPath)) {
    fwrite(STDERR, "CA Certificate file not found: {$caPath}\n");
    exit(1);
}
$content = file_get_contents($caPath);
if (strpos($content, '-----BEGIN CERTIFICATE-----') === false) {
    fwrite(STDERR, "Invalid CA Certificate format in {$caPath}\n");
    exit(1);
}
echo "CA Certificate verified successfully.\n";
exit(0);
