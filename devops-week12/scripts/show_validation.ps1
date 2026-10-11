$Host.UI.RawUI.WindowTitle = 'Week 12 - Local Verification'
Clear-Host
Write-Host 'DEVOPS WEEK 12 - ACTUAL LOCAL VALIDATION' -ForegroundColor Cyan
Get-Date -Format o
wsl.exe -d Ubuntu --exec bash -lc 'cd ~/devops-week1 && devops-week12/.venv/bin/pytest -q devops-week12/tests/test_services.py && helm lint devops-week12/chart && bash -n devops-week12/scripts/bootstrap.sh && git diff --check'
if ($LASTEXITCODE -ne 0) { Write-Host 'Local check failed' -ForegroundColor Red; exit $LASTEXITCODE }
Write-Host 'Local service tests and chart validation: PASSED' -ForegroundColor Green
Write-Host 'CI: 5 successful jobs, run 38113483248' -ForegroundColor Green
Write-Host 'Live end-to-end deployment: NOT VERIFIED' -ForegroundColor Yellow
Write-Host 'Blocker: repeated WSL runtime failures during cluster startup/image pulls.' -ForegroundColor Yellow
Write-Host 'ArgoCD, Kong, monitoring, canary and fresh-cluster checks remain pending.'
