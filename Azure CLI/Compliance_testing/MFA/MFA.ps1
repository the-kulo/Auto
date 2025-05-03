[CmdletBinding()]
param (
    [Parameter(Position=0, ValueFromPipeline=$true, ValueFromPipelineByPropertyName=$true)]
    [string[]]$UserPrincipalName,
    [int]$MaxResults = 10000
)

BEGIN {
    $AdminUsers = Get-MsolRoleMember -RoleObjectId '62e90394-69f5-4237-9190-012177145e10' -ErrorAction Stop | Select-Object EmailAddress -Unique
}

PROCESS {
    if ($UserPrincipalName) {
        foreach ($User in $UserPrincipalName) {
            try {
                Get-MsolUser -UserPrincipalName $User -ErrorAction Stop | 
                Select-Object DisplayName, UserPrincipalName, IsLicensed,
                @{Name='isCompanyAdmin'; Expression={ if ($AdminUsers -match $_.UserPrincipalName) { $true } else { $false } } },
                @{Name='MFAEnabled'; Expression={ 
                    if ($_.StrongAuthenticationRequirements.State -eq "Enabled") { $true }
                    elseif ($null -ne $_.StrongAuthenticationMethods.MethodType) { $true }
                    else { $false }
                }},
                @{Name='AuthenticationMethods'; Expression={
                    $_.StrongAuthenticationMethods | ForEach-Object {
                        $_.MethodType
                    }
                }},
                @{Name='MFAPhone'; Expression={
                    if ($_.StrongAuthenticationRequirements.State -eq "Enabled" -or $null -ne $_.StrongAuthenticationMethods) {
                        $_.StrongAuthenticationUserDetails.PhoneNumber
                    } else {
                        $null
                    }
                }}
            } catch {
                $Object = [pscustomobject]@{
                    DisplayName = '_NotSynced'
                    UserPrincipalName = $User
                    IsLicensed = $false
                    isCompanyAdmin = '-'
                    MFAEnabled = '-'
                    AuthenticationMethods = '-'
                    MFAPhone = '-'
                }
                Write-Output $Object
            }
        }
    } else {
        $AllUsers = Get-MsolUser -MaxResults $MaxResults | 
        Select-Object DisplayName, UserPrincipalName, LastDirSyncTime, LastPasswordChangeTimestamp, ObjectId, ValidationStatus, WhenCreated, IsLicensed,
        @{Name='isCompanyAdmin'; Expression={ if ($AdminUsers -match $_.UserPrincipalName) { $true } else { $false } } },
        @{Name='MFAEnabled'; Expression={ 
            if ($_.StrongAuthenticationRequirements.State -eq "Enabled") { $true }
            elseif ($null -ne $_.StrongAuthenticationMethods.MethodType) { $true }
            else { $false }
        }},
        @{Name='AuthenticationMethods'; Expression={
            $_.StrongAuthenticationMethods | ForEach-Object {
                $_.MethodType
            }
        }},
        @{Name='MFAPhone'; Expression={
            if ($_.StrongAuthenticationRequirements.State -eq "Enabled" -or $null -ne $_.StrongAuthenticationMethods) {
                $_.StrongAuthenticationUserDetails.PhoneNumber
            } else {
                $null
            }
        }}
    }
}

END {
    if ($null -ne $AllUsers) {
        $path = [Environment]::GetFolderPath("Desktop") + "\" + "input" + ".csv"
        $AllUsers | Export-Csv -LiteralPath $path -NoTypeInformation -Force -Encoding UTF8
        Write-Output "$(Get-Date) * Please check $path"
    } elseif (!$UserPrincipalName) {
        Write-Output "$(Get-Date) * User information not found."
    }
}