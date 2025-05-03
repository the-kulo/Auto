@description('CPU警报规则名称')
@minLength(1)
@maxLength(260)
param alertNameCPU string = 'HighCPUAlert'

@description('内存警报名称')
param alertNameMemory string = 'HighMemoryAlert'

@description('磁盘空间警报名称')
param alertNameDiskSpace string = 'LowDiskSpaceAlert'

@description('IOPS警报名称')
param alertNameIOPS string = 'HighIOPSAlert'

@description('目标虚拟机资源ID')
param targetResourceId string

@description('操作组资源ID')
param actionGroupId string

@description('CPU使用率阈值百分比')
@minValue(0)
@maxValue(100)
param cpuThreshold int = 90

@description('内存使用率阈值百分比')
@minValue(0)
@maxValue(100)
param memoryThreshold int = 90

@description('磁盘剩余空间阈值百分比')
@minValue(0)
@maxValue(100)
param diskSpaceThreshold int = 10

@description('IOPS消耗百分比阈值')
@minValue(0)
@maxValue(100)
param iopsThreshold int = 95

@description('警报严重性:0=关键,1=错误,2=警告,3=信息,4=详细')
@allowed([
  0
  1
  2
  3
  4
])
param severity int = 2

var vmMetricNamespace = 'Microsoft.Compute/virtualMachines'

resource alertNameCPU_resource 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: alertNameCPU
  location: 'global'
  properties: {
    description: 'CPU使用率超过${cpuThreshold}%时触发'
    severity: severity
    enabled: true
    scopes: [
      targetResourceId
    ]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          criterionType: 'StaticThresholdCriterion'
          name: 'HighCPU'
          metricNamespace: vmMetricNamespace
          metricName: 'Percentage CPU'
          dimensions: []
          operator: 'GreaterThan'
          threshold: cpuThreshold
          timeAggregation: 'Average'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroupId
      }
    ]
  }
}

resource alertNameMemory_resource 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: alertNameMemory
  location: 'global'
  properties: {
    description: '内存使用超过${memoryThreshold}%时触发'
    severity: severity
    enabled: true
    scopes: [
      targetResourceId
    ]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          criterionType: 'StaticThresholdCriterion'
          name: 'HighMemoryUsage'
          metricNamespace: vmMetricNamespace
          metricName: 'Available Memory Bytes'
          operator: 'LessThan'
          threshold: memoryThreshold
          timeAggregation: 'Average'
          dimensions: []
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroupId
      }
    ]
  }
}

resource alertNameDiskSpace_resource 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: alertNameDiskSpace
  location: 'global'
  properties: {
    description: '磁盘剩余空间低于${diskSpaceThreshold}%时触发'
    severity: severity
    enabled: true
    scopes: [
      targetResourceId
    ]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          criterionType: 'StaticThresholdCriterion'
          name: 'LowDiskSpace'
          metricNamespace: vmMetricNamespace
          metricName: 'Disk Read Operations/Sec'
          operator: 'GreaterThan'
          threshold: diskSpaceThreshold
          timeAggregation: 'Average'
          dimensions: []
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroupId
      }
    ]
  }
}

resource alertNameIOPS_resource 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: alertNameIOPS
  location: 'global'
  properties: {
    description: 'IOPS消耗超过${iopsThreshold}%时触发'
    severity: severity
    enabled: true
    scopes: [
      targetResourceId
    ]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          criterionType: 'StaticThresholdCriterion'
          name: 'HighIOPSUsage'
          metricNamespace: 'Microsoft.Compute/virtualMachines'
          metricName: 'Data Disk IOPS Consumed Percentage'
          operator: 'GreaterThan'
          threshold: iopsThreshold
          timeAggregation: 'Average'
          dimensions: []
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroupId
      }
    ]
  }
}
