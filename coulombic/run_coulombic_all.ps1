# run_coulombic_all.ps1
# run_coulombic_all.ps1
$py  = "python"
$runner = ".\run_cxc_on_cxs_1.3.py"
$cxc = "..\cxc_scripts\coulombic.cxc"

# IDs (runid_jobid) -> we build the wildcard "..\setup\<ID>*.cxs"
$ids = @(
  "0084_02",
  "0097_01",
  "0097_08"
)

$patterns = $ids | ForEach-Object { "..\setup\$($_)*.cxs" }

# How many times to retry when output wasn't created
$maxTries = 3
$delaySec = 2

function Get-OutPath($inPath, $cxcPath) {
  $wd = (Get-Location).Path
  $cxcBase = [IO.Path]::GetFileNameWithoutExtension($cxcPath)

  $name = [IO.Path]::GetFileName($inPath)
  $m = [regex]::Match($name, "^\d{4}_\d{2}")
  $prefix = if ($m.Success) { $m.Value } else { [IO.Path]::GetFileNameWithoutExtension($inPath) }

  return Join-Path $wd ("{0}_{1}.cxs" -f $prefix, $cxcBase)
}

$inputs = foreach ($p in $patterns) { Get-ChildItem -File $p -ErrorAction SilentlyContinue }
if (-not $inputs) { throw "No input .cxs matched your ID patterns." }

foreach ($f in $inputs) {
  $inPath  = $f.FullName
  $outPath = Get-OutPath $inPath $cxc

  Write-Host "`n=== $($f.Name) ==="
  for ($try=1; $try -le $maxTries; $try++) {
    Write-Host "Try $try/$maxTries"
    & $py $runner $inPath $cxc

    if (Test-Path $outPath) {
      Write-Host "[OK] Output exists: $outPath"
      break
    } else {
      Write-Warning "[WARN] Output missing: $outPath"
      if ($try -lt $maxTries) { Start-Sleep -Seconds $delaySec }
    }
  }

  if (-not (Test-Path $outPath)) {
    Write-Error "[FAIL] Still no output after $maxTries tries for $($f.Name)"
  }
}
