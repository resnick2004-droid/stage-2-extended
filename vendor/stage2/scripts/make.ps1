<#
.SYNOPSIS
    Windows equivalent of the Makefile targets (make does not ship with Windows).

.EXAMPLE
    .\scripts\make.ps1 verify

.DESCRIPTION
    Targets: test, test-fast, verify, vendor-integrity, vendor-tests, manifest, stage-manifest, hooks, status, clean.

    test-fast is the commit-time fast tier (R10), -m "not slow and not heavy", as scripts/pre-commit runs it.
    verify runs everything, as CI does (.github/workflows/verify.yml).

    Hashing follows the platform: sha256sum on Linux, shasum -a 256 on macOS. Neither ships
    with Windows, so scripts/hashes.py (hashlib) is used here. It writes and checks the same
    native sha256sum manifest format, so a manifest made on Windows verifies on Linux and
    macOS with their own tools.
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('help', 'test', 'test-fast', 'verify','vendor-integrity', 'vendor-tests', 'manifest', 'stage-manifest', 'hooks', 'status', 'clean')]
    [string]$Target = 'help'
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Python = if ($env:PYTHON) { $env:PYTHON } else { 'python' }
$VendorManifest = Join-Path $Root 'vendor\MANIFEST.sha256'

# Keep the read-only vendored tree free of .pyc files (D-01).
$env:PYTHONDONTWRITEBYTECODE = '1'

function Invoke-Step {
    param([string]$Name, [scriptblock]$Body)
    Write-Host "--- $Name ---" -ForegroundColor Cyan
    # Out-Host keeps each step's output with its own header; without it PowerShell buffers
    # the native commands' stdout and prints every header before any of the output.
    & $Body 2>&1 | Out-Host
    if ($LASTEXITCODE -ne 0) {
        Write-Host "$Name FAILED (exit $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

Push-Location $Root
try {
    switch ($Target) {
        'help' {
            Write-Host "test              run the stage-two test suite (all of it)"
            Write-Host "test-fast         the fast tier only (-m `"not slow and not heavy`"), as the pre-commit hook runs it"
            Write-Host "verify            vendor integrity + stage-two suite + vendored stage-one suite (everything; CI runs this)"
            Write-Host "vendor-integrity  check vendor/propsim against vendor/MANIFEST.sha256"
            Write-Host "vendor-tests      run stage one's own suite from the vendored location"
            Write-Host "manifest          regenerate vendor/MANIFEST.sha256"
            Write-Host "stage-manifest    write STAGE_MANIFEST.sha256 from the committed tree (the close's manifest)"
            Write-Host "hooks             install scripts/pre-commit as the git pre-commit hook"
            Write-Host "status            open tasks, pre-registrations, unverified rules, last test run"
        }
        'test' {
            Invoke-Step 'stage-two tests' { & $Python -m pytest -o addopts= -q }
        }
        'test-fast' {
            Invoke-Step 'stage-two tests, fast tier' { & $Python -m pytest -o addopts= -q -m 'not slow and not heavy' }
        }
        'vendor-integrity' {
            Invoke-Step 'vendor integrity' { & $Python scripts\hashes.py check $VendorManifest }
        }
        'vendor-tests' {
            Invoke-Step 'vendored stage-one suite (expect 33 passed)' {
                Push-Location (Join-Path $Root 'vendor\propsim')
                try { & $Python -m pytest test_propsim.py -o addopts= -q -p no:cacheprovider } finally { Pop-Location }
            }
        }
        'verify' {
            Invoke-Step 'vendor integrity' { & $Python scripts\hashes.py check $VendorManifest }
            Invoke-Step 'stage-two tests' { & $Python -m pytest -o addopts= -q }
            Invoke-Step 'vendored stage-one suite (expect 33 passed)' {
                Push-Location (Join-Path $Root 'vendor\propsim')
                try { & $Python -m pytest test_propsim.py -o addopts= -q -p no:cacheprovider } finally { Pop-Location }
            }
            Write-Host "--- verify complete ---" -ForegroundColor Green
        }
        'manifest' {
            Invoke-Step 'regenerate vendor manifest' {
                & $Python scripts\hashes.py write vendor\propsim $VendorManifest
            }
        }
        'stage-manifest' {
            Invoke-Step 'write the stage manifest' { & $Python scripts\stage_manifest.py write }
        }
        'hooks' {
            Invoke-Step 'install git hooks' { & $Python scripts\install_hooks.py }
        }
        'status' {
            & $Python scripts\status.py
        }
        'clean' {
            Get-ChildItem -Path $Root -Recurse -Directory -Filter '__pycache__' -ErrorAction SilentlyContinue |
                Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
            $pc = Join-Path $Root '.pytest_cache'
            if (Test-Path $pc) { Remove-Item $pc -Recurse -Force }
            Write-Host "cleaned" -ForegroundColor Green
        }
    }
}
finally {
    Pop-Location
}
