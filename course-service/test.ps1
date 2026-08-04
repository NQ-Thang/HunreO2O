$ErrorActionPreference = 'SilentlyContinue'
echo "1. POST /courses"
$r1 = Invoke-RestMethod -Uri http://localhost:8082/courses -Method Post -ContentType "application/json" -Body '{"tenMonHoc":"Lap trinh Java","soTinChi":3,"soChoToiDa":40}'
$r1 | ConvertTo-Json

echo "2. GET /courses"
$r2 = Invoke-RestMethod -Uri http://localhost:8082/courses -Method Get
$r2 | ConvertTo-Json

echo "3. GET /courses/1"
$r3 = Invoke-RestMethod -Uri http://localhost:8082/courses/1 -Method Get
$r3 | ConvertTo-Json

echo "4. PUT /courses/1"
$r4 = Invoke-RestMethod -Uri http://localhost:8082/courses/1 -Method Put -ContentType "application/json" -Body '{"tenMonHoc":"Lap trinh Java Advanced","soTinChi":4,"soChoToiDa":50}'
$r4 | ConvertTo-Json

echo "5. DELETE /courses/1"
$r5 = Invoke-WebRequest -Uri http://localhost:8082/courses/1 -Method Delete
$r5.StatusCode

echo "6. POST BAD REQUEST (Empty Name)"
try {
    Invoke-RestMethod -Uri http://localhost:8082/courses -Method Post -ContentType "application/json" -Body '{"tenMonHoc":"","soTinChi":3,"soChoToiDa":40}'
} catch {
    $_.Exception.Response.StatusCode
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $reader.ReadToEnd()
}

echo "7. POST BAD REQUEST (Duplicate Name)"
Invoke-RestMethod -Uri http://localhost:8082/courses -Method Post -ContentType "application/json" -Body '{"tenMonHoc":"Co So Du Lieu","soTinChi":3,"soChoToiDa":40}' > $null
try {
    Invoke-RestMethod -Uri http://localhost:8082/courses -Method Post -ContentType "application/json" -Body '{"tenMonHoc":"Co So Du Lieu","soTinChi":3,"soChoToiDa":40}'
} catch {
    $_.Exception.Response.StatusCode
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $reader.ReadToEnd()
}
