[CmdletBinding()]
param (
    [Parameter(Mandatory = $false)]
    [string]$UserPrincipalName,

    [Parameter(Mandatory = $false)]
    [switch]$ExportToCsv
)

function Test-ExchangeConnection {
    try {
        # Test connection
        $null = Get-EXOMailbox -ResultSize 1 -ErrorAction Stop
        return $true
    } catch {
        Write-Warning "Not connected to Exchange Online. Please run: Connect-ExchangeOnline -ExchangeEnvironmentName O365China"
        return $false
    }
} # end Test-ExchangeConnection

function Get-QuickDeviceInfo {
    param(
        [string]$UPN
    )

    $results = @()

    try {
        if ($UPN) {
            Write-Host "Getting device information for user $UPN..." -ForegroundColor Yellow
            $mailboxes = @(Get-EXOMailbox -Identity $UPN -ErrorAction Stop)
        } else {
            Write-Host "Getting device information for all users..." -ForegroundColor Yellow
            $mailboxes = Get-EXOMailbox -ResultSize Unlimited -RecipientTypeDetails UserMailbox
        }

        $totalUsers  = $mailboxes.Count
        $currentUser = 0

        foreach ($mailbox in $mailboxes) {
            $currentUser++
            if ($totalUsers -gt 1) {
                Write-Progress -Activity "Scanning user devices" `
                               -Status "$($mailbox.DisplayName) ($currentUser/$totalUsers)" `
                               -PercentComplete (($currentUser / $totalUsers) * 100)
            }

            try {
                $devices = Get-EXOMobileDeviceStatistics -Mailbox $mailbox.UserPrincipalName -ErrorAction SilentlyContinue
                foreach ($device in $devices) {
                    $results += [PSCustomObject]@{
                        User            = $mailbox.DisplayName
                        UPN             = $mailbox.UserPrincipalName
                        'Device Model'  = $device.DeviceModel
                        'Device OS'     = $device.DeviceOS
                        'User Agent'    = $device.DeviceUserAgent
                        'Device Type'   = $device.DeviceType
                        'Device ID'     = $device.DeviceId
                    }
                }
            } catch {
                Write-Warning "Unable to get device information for $($mailbox.UserPrincipalName): $($_.Exception.Message)"
            }
        }

        if ($totalUsers -gt 1) {
            Write-Progress -Activity "Scanning user devices" -Completed
        }
    } catch {
        Write-Error "Error getting device information: $($_.Exception.Message)"
    }

    return $results
} # end Get-QuickDeviceInfo

function Export-QuickReport {
    param(
        [array]$DeviceData
    )

    if ($DeviceData.Count -eq 0) {
        Write-Host "No data to export" -ForegroundColor Yellow
        return
    }

    try {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $fileName  = "Mobile_Device_Report_$timestamp.csv"
        $desktopPath = [Environment]::GetFolderPath("Desktop")
        $filePath  = Join-Path $desktopPath $fileName

        $DeviceData | Export-Csv -Path $filePath -NoTypeInformation -Encoding UTF8
        Write-Host "Report exported to $filePath" -ForegroundColor Green

        if (Test-Path $filePath) {
            Start-Process -FilePath "explorer.exe" -ArgumentList "/select,$filePath"
        }
    } catch {
        Write-Error "Error exporting file: $($_.Exception.Message)"
    }
} # end Export-QuickReport

function Main {
    Write-Host "Mobile Device Report Tool" -ForegroundColor Cyan

    if (-not (Test-ExchangeConnection)) {
        Write-Host "Please connect to Exchange Online first: Connect-ExchangeOnline -ExchangeEnvironmentName O365China" -ForegroundColor Red
        return
    }

    Write-Host "Exchange Online connection is normal" -ForegroundColor Green

    $deviceData = Get-QuickDeviceInfo -UPN $UserPrincipalName

    if ($deviceData.Count -eq 0) {
        Write-Host "No mobile devices found" -ForegroundColor Yellow
        return
    }

    Write-Host "Found $($deviceData.Count) devices" -ForegroundColor Green
    $deviceData | Format-Table -AutoSize

    if ($ExportToCsv) {
        Export-QuickReport -DeviceData $deviceData
    } else {
        Write-Host "Use -ExportToCsv parameter to export results to CSV file" -ForegroundColor Cyan
    }
} 

# Entry point
Main
