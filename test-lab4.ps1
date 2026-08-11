$adminJson = curl.exe -s -X POST http://localhost:8081/auth/login -H "Content-Type: application/json" -d '{\"username\":\"admin\", \"password\":\"admin123\"}'
$adminToken = ($adminJson | ConvertFrom-Json).token
$studentJson = curl.exe -s -X POST http://localhost:8081/auth/login -H "Content-Type: application/json" -d '{\"username\":\"student1\", \"password\":\"student123\"}'
$studentToken = ($studentJson | ConvertFrom-Json).token

Write-Host "`n--- TEST 2.2: Gateway Public API (no token) GET /api/courses ---"
curl.exe -s -i http://localhost:8080/api/courses | Select-String "HTTP/"

Write-Host "`n--- TEST 2.3: Gateway Block No Token POST /api/courses ---"
curl.exe -s -i -X POST http://localhost:8080/api/courses -H "Content-Type: application/json" -d '{\"tenMonHoc\":\"abc\",\"soTinChi\":3,\"soChoToiDa\":30}' | Select-String "HTTP/"

Write-Host "`n--- TEST 2.4: Gateway Role Deny POST /api/courses (Student Token) ---"
curl.exe -s -i -X POST http://localhost:8080/api/courses -H "Authorization: Bearer $studentToken" -H "Content-Type: application/json" -d '{\"tenMonHoc\":\"abc\",\"soTinChi\":3,\"soChoToiDa\":30}' | Select-String "HTTP/"

Write-Host "`n--- TEST 2.5: Gateway Role Allow POST /api/courses (Admin Token) ---"
curl.exe -s -i -X POST http://localhost:8080/api/courses -H "Authorization: Bearer $adminToken" -H "Content-Type: application/json" -d '{\"tenMonHoc\":\"def\",\"soTinChi\":3,\"soChoToiDa\":30}' | Select-String "HTTP/"

Write-Host "`n--- TEST 2.6: Gateway Cross Service POST /api/registrations (Student Token) ---"
curl.exe -s -i -X POST http://localhost:8080/api/registrations -H "Authorization: Bearer $studentToken" -H "Content-Type: application/json" -d '{\"studentId\":1, \"courseId\":2}' | Select-String "HTTP/"

Write-Host "`n--- TEST 2.7: Gateway API Key (Valid) GET /api/public/courses ---"
curl.exe -s -i GET http://localhost:8080/api/public/courses -H "X-API-KEY: crs-partner-key-2026" | Select-String "HTTP/"

Write-Host "`n--- TEST 2.8: Gateway API Key (Invalid) GET /api/public/courses ---"
curl.exe -s -i GET http://localhost:8080/api/public/courses -H "X-API-KEY: sai-key" | Select-String "HTTP/"
