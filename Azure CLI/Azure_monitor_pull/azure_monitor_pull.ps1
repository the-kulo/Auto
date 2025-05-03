# 适用于较小资源组的周指标review
# use with azure cli
Login-AzAccount -Environment Azurecloud

$startTime = (Get-Date).AddDays(-(Get-Date).DayOfWeek.value__ - 6).Date
$endTime = $startTime.AddDays(6).AddHours(23).AddMinutes(59).AddSeconds(59)

$resources = @(
    "/subscriptions/xxx"
)

$metrics = @("cpu_percent", "memory_percent")

$output = @()

Write-Host "start time: $startTime"
Write-Host "end time: $endTime"

foreach ($resource in $resources) {
    $resourceName = ($resource -split '/')[($resource -split '/').Length - 1]

    Write-Host "Resource name: $resourceName"

    foreach ($metric in $metrics) {
        $maxOutput = az monitor metrics list --resource $resource --metric $metric --start-time $startTime.ToUniversalTime().ToString("o") --end-time $endTime.ToUniversalTime().ToString("o") --aggregation Maximum --interval "PT5M" --output json     
        $metricsData = $maxOutput | ConvertFrom-Json
        $overallMax = 0

        foreach ($timeSeries in $metricsData.value[0].timeseries) {
            foreach ($dataPoint in $timeseries.data) {
                # Write-Host $dataPoint
                if ($dataPoint.maximum -gt $overallMax) {
                    $overallMax = $dataPoint.maximum
                }
            }
        }

        $maxValue = $overallMax

        $avgOutput = az monitor metrics list --resource $resource --metric $metric --start-time $startTime.ToUniversalTime().ToString("o") --end-time $endTime.ToUniversalTime().ToString("o") --aggregation Average --interval "PT5M" --output json
        $metricsData = $avgOutput | ConvertFrom-Json

        $sum = 0
        $count = 0

        foreach ($timeSeries in $metricsData.value[0].timeseries) {
            foreach ($dataPoint in $timeseries.data) {
            $sum += $dataPoint.average
            $count++
            }
        }

        $avgValue = [Math]::Round($sum / $count, 2)

        $output += [PSCustomObject]@{
            Resource = $resourceName
            Metric = $metric
            MaxValue = $maxValue
            AvgValue = $avgValue
        }
    }
}

$output | Format-Table -Property Resource, Metric, MaxValue, AvgValue
