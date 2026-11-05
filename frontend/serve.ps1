<#
.SYNOPSIS
  Lightweight local HTTP server for PayPilot AI Frontend (Meenal's Work).
.DESCRIPTION
  Runs an HTTP listener on http://127.0.0.1:3000 to preview the frontend UI
  and test live connectivity to the Flask backend running on port 5001.
#>

param(
  [int]$Port = 3000
)

$listener = New-Object System.Net.HttpListener
$prefix = "http://localhost:$Port/"
$listener.Prefixes.Add($prefix)

try {
  $listener.Start()
  Write-Host "==========================================================" -ForegroundColor Cyan
  Write-Host "🚀 PayPilot AI Frontend Server (Meenal)" -ForegroundColor Green
  Write-Host "   URL: http://localhost:$Port/index.html" -ForegroundColor Yellow
  Write-Host "   Tests: http://localhost:$Port/tests/run_tests.html" -ForegroundColor Yellow
  Write-Host "   Backend API Target: http://127.0.0.1:5001" -ForegroundColor Gray
  Write-Host "==========================================================" -ForegroundColor Cyan
  Write-Host "Press Ctrl+C to stop the server.`n"

  while ($listener.IsListening) {
    $context = $listener.GetContext()
    $request = $context.Request
    $response = $context.Response

    $path = $request.Url.LocalPath.TrimStart('/')
    if ([string]::IsNullOrWhiteSpace($path)) { $path = "index.html" }

    $localPath = Join-Path $PSScriptRoot $path

    if (Test-Path $localPath -PathType Leaf) {
      $ext = [System.IO.Path]::GetExtension($localPath).ToLower()
      $contentType = switch ($ext) {
        ".html" { "text/html; charset=utf-8" }
        ".css"  { "text/css; charset=utf-8" }
        ".js"   { "application/javascript; charset=utf-8" }
        ".json" { "application/json; charset=utf-8" }
        ".png"  { "image/png" }
        ".jpg"  { "image/jpeg" }
        ".svg"  { "image/svg+xml" }
        default { "application/octet-stream" }
      }

      $bytes = [System.IO.File]::ReadAllBytes($localPath)
      $response.ContentType = $contentType
      $response.ContentLength64 = $bytes.Length
      $response.StatusCode = 200
      $response.OutputStream.Write($bytes, 0, $bytes.Length)
    } else {
      $response.StatusCode = 404
      $msg = [System.Text.Encoding]::UTF8.GetBytes("404 Not Found: $path")
      $response.OutputStream.Write($msg, 0, $msg.Length)
    }

    $response.OutputStream.Close()
  }
} finally {
  $listener.Stop()
}
