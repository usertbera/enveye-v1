$AppName = "enveye-agent"
$SourceFile = "main.go"

Write-Host "🚧 Building $AppName for multiple platforms..."

$Targets = @(
    @{ GOOS = "windows"; GOARCH = "amd64"; Extension = ".exe" },
    @{ GOOS = "linux";   GOARCH = "amd64"; Extension = "" },
    @{ GOOS = "darwin";  GOARCH = "amd64"; Extension = "" },
    @{ GOOS = "darwin";  GOARCH = "arm64"; Extension = "" }
)

foreach ($target in $Targets) {
    $GOOS = $target.GOOS
    $GOARCH = $target.GOARCH
    $Ext = $target.Extension

    $OutputDir = "dist\$GOOS`_$GOARCH"
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

    $OutputPath = "$OutputDir\$AppName$Ext"

    Write-Host "🔨 Building for $GOOS/$GOARCH..."
    $env:GOOS = $GOOS
    $env:GOARCH = $GOARCH

    go build -o $OutputPath $SourceFile

    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Build failed for $GOOS/$GOARCH" -ForegroundColor Red
    } else {
        Write-Host "✅ Built: $OutputPath"
    }
}

Write-Host "`n✅ All builds completed! Binaries are in the dist\ directory." -ForegroundColor Green
