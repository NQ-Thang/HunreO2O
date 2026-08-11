$ErrorActionPreference = "SilentlyContinue"

Write-Host "==========================================="
Write-Host " TEST DATA CREATION (NGUYEN VAN CHIEN - DH13C1)"
Write-Host "==========================================="
$rnd = Get-Random -Minimum 1000 -Maximum 9999
$courseName = "Lap trinh Java Nang Cao $rnd"
$body = @{ tenMonHoc = $courseName; soTinChi = 3; soChoToiDa = 2 } | ConvertTo-Json
$courseRes = Invoke-RestMethod -Method Post -Uri "http://localhost:8082/courses" -ContentType "application/json" -Body $body
$courseId = $courseRes.id
Write-Host "Created Course ID: $courseId, Max Seats: 2" -ForegroundColor Green

Write-Host "`n--- TEST 1: Reserve seat ---"
$res1 = Invoke-RestMethod -Method Patch -Uri "http://localhost:8082/internal/courses/$courseId/reserve-seat"
Write-Host "Result (Remaining seats must be 1): soChoConLai = $($res1.soChoConLai)" -ForegroundColor Cyan

Write-Host "`n--- TEST 2: Reserve until 0 (Out of seats) ---"
Invoke-RestMethod -Method Patch -Uri "http://localhost:8082/internal/courses/$courseId/reserve-seat" | Out-Null
Write-Host "Reserved 1 more seat. Seats are now 0. Trying to reserve again..."
try {
    Invoke-RestMethod -Method Patch -Uri "http://localhost:8082/internal/courses/$courseId/reserve-seat" -ErrorAction Stop
} catch {
    $errBody = $_.Exception.Response.GetResponseStream() | %{ (New-Object System.IO.StreamReader($_)).ReadToEnd() }
    Write-Host "Error received: $errBody (Expected 409 Conflict)" -ForegroundColor Yellow
}

Write-Host "`n--- TEST 3: Release seat ---"
$res3 = Invoke-RestMethod -Method Patch -Uri "http://localhost:8082/internal/courses/$courseId/release-seat"
Write-Host "Result (Remaining seats must be 1): soChoConLai = $($res3.soChoConLai)" -ForegroundColor Cyan

Write-Host "`n--- TEST 4: Successful Registration (Via API port 8083) ---"
$regBody = @{ studentId = 1; courseId = $courseId } | ConvertTo-Json
$regRes = Invoke-RestMethod -Method Post -Uri "http://localhost:8083/registrations" -ContentType "application/json" -Body $regBody
$regId = $regRes.id
Write-Host "Registered successfully, Registration ID: $regId, Status: $($regRes.trangThai)" -ForegroundColor Green

Write-Host "`n--- TEST 5: Duplicate Registration ---"
try {
    Invoke-RestMethod -Method Post -Uri "http://localhost:8083/registrations" -ContentType "application/json" -Body $regBody -ErrorAction Stop
} catch {
    $errBody = $_.Exception.Response.GetResponseStream() | %{ (New-Object System.IO.StreamReader($_)).ReadToEnd() }
    Write-Host "Error received: $errBody (Expected duplicate 409 Conflict)" -ForegroundColor Yellow
}

Write-Host "`n--- TEST 6: Cancel Registration ---"
Invoke-RestMethod -Method Delete -Uri "http://localhost:8083/registrations/$regId"
Write-Host "Sent delete request for Registration ID: $regId (Expected Status 200/204)" -ForegroundColor Cyan

Write-Host "`n--- TEST 7: Register for non-existent course (courseId = 9999) ---"
$regBodyInvalid = @{ studentId = 2; courseId = 9999 } | ConvertTo-Json
try {
    Invoke-RestMethod -Method Post -Uri "http://localhost:8083/registrations" -ContentType "application/json" -Body $regBodyInvalid -ErrorAction Stop
} catch {
    $errBody = $_.Exception.Response.GetResponseStream() | %{ (New-Object System.IO.StreamReader($_)).ReadToEnd() }
    Write-Host "Error received: $errBody (Expected 404/409 Course not found)" -ForegroundColor Yellow
}

Write-Host "`n--- TEST 8: Search with Keyword (Lap trinh) ---"
$searchRes = Invoke-RestMethod -Method Get -Uri "http://localhost:8082/courses?keyword=Lap%20trinh&page=0&size=5"
Write-Host "Number of items found: $($searchRes.content.Count)" -ForegroundColor Cyan

Write-Host "`n--- TEST 9: Invalid pagination param (page = -1) ---"
try {
    Invoke-RestMethod -Method Get -Uri "http://localhost:8082/courses?page=-1" -ErrorAction Stop
} catch {
    $errBody = $_.Exception.Response.GetResponseStream() | %{ (New-Object System.IO.StreamReader($_)).ReadToEnd() }
    Write-Host "Error received: $errBody (Expected 400 Bad Request/500)" -ForegroundColor Yellow
}

Write-Host "`n--- TEST 10: Sort by non-existent field ---"
try {
    Invoke-RestMethod -Method Get -Uri "http://localhost:8082/courses?sort=truongKhongTonTai,asc" -ErrorAction Stop
} catch {
    $errBody = $_.Exception.Response.GetResponseStream() | %{ (New-Object System.IO.StreamReader($_)).ReadToEnd() }
    Write-Host "Error received (Expected PropertyReferenceException)" -ForegroundColor Yellow
}

Write-Host "`n--- TEST 11: Cancel registration twice ---"
try {
    Invoke-RestMethod -Method Delete -Uri "http://localhost:8083/registrations/$regId" -ErrorAction Stop
} catch {
    $errBody = $_.Exception.Response.GetResponseStream() | %{ (New-Object System.IO.StreamReader($_)).ReadToEnd() }
    Write-Host "Error on 2nd time: $errBody (Expected 409 Already cancelled)" -ForegroundColor Yellow
}

Write-Host "`n--- TEST 12: Validation input (Missing courseId) ---"
$badBody = @{ studentId = 1 } | ConvertTo-Json
try {
    Invoke-RestMethod -Method Post -Uri "http://localhost:8083/registrations" -ContentType "application/json" -Body $badBody -ErrorAction Stop
} catch {
    $errBody = $_.Exception.Response.GetResponseStream() | %{ (New-Object System.IO.StreamReader($_)).ReadToEnd() }
    Write-Host "Validation Error: $errBody (Expected 400 Bad Request)" -ForegroundColor Yellow
}

Write-Host "`n==========================================="
Write-Host " FINISHED RUNNING AUTOMATED TESTS"
Write-Host "==========================================="
