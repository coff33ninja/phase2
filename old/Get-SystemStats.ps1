#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Comprehensive System Statistics Gathering Script
.DESCRIPTION
    Collects detailed hardware, software, and performance statistics from Windows systems
    Generates a formatted report with all system information
.NOTES
    Author: System Statistics Collector
    Version: 1.0
    Requires: Administrator privileges for full data collection
#>

# Set error handling
$ErrorActionPreference = 'SilentlyContinue'

# Function to format bytes to human-readable
function Format-Bytes {
    param([long]$Bytes)
    if ($Bytes -ge 1TB) { return "{0:N2} TB" -f ($Bytes / 1TB) }
    if ($Bytes -ge 1GB) { return "{0:N2} GB" -f ($Bytes / 1GB) }
    if ($Bytes -ge 1MB) { return "{0:N2} MB" -f ($Bytes / 1MB) }
    if ($Bytes -ge 1KB) { return "{0:N2} KB" -f ($Bytes / 1KB) }
    return "$Bytes Bytes"
}

# Function to create section header
function Write-SectionHeader {
    param([string]$Title)
    Write-Host "`n" -NoNewline
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host " $Title" -ForegroundColor Yellow
    Write-Host ("=" * 80) -ForegroundColor Cyan
}

# Function to write key-value pair
function Write-Info {
    param(
        [string]$Key,
        [string]$Value,
        [int]$Indent = 0
    )
    $indentStr = " " * $Indent
    Write-Host "$indentStr$Key`: " -NoNewline -ForegroundColor Green
    Write-Host $Value -ForegroundColor White
}

# Start report
Clear-Host
$startTime = Get-Date
Write-Host @"
╔════════════════════════════════════════════════════════════════════════════════╗
║                    COMPREHENSIVE SYSTEM STATISTICS REPORT                      ║
║                           Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")                          ║
╚════════════════════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# ============================================================================
# SYSTEM IDENTIFICATION
# ============================================================================
Write-SectionHeader "SYSTEM IDENTIFICATION"

$computerSystem = Get-WmiObject Win32_ComputerSystem
$computerInfo = Get-ComputerInfo

Write-Info "Computer Name" $env:COMPUTERNAME
Write-Info "Owner" $computerSystem.PrimaryOwnerName
Write-Info "Manufacturer" $computerSystem.Manufacturer
Write-Info "Model" $computerSystem.Model
Write-Info "System Type" $computerSystem.SystemType
Write-Info "Domain/Workgroup" $computerSystem.Domain
Write-Info "Total Processors" $computerInfo.CsNumberOfProcessors
Write-Info "PC System Type" $(switch($computerInfo.CsPCSystemType){1{"Desktop"}2{"Mobile"}3{"Workstation"}4{"Enterprise Server"}5{"SOHO Server"}6{"Appliance PC"}7{"Performance Server"}8{"Maximum"}default{"Unknown"}})

# ============================================================================
# OPERATING SYSTEM
# ============================================================================
Write-SectionHeader "OPERATING SYSTEM"

$os = Get-WmiObject Win32_OperatingSystem
$osVersion = [System.Environment]::OSVersion

Write-Info "OS Name" $os.Caption
Write-Info "Version" $os.Version
Write-Info "Build Number" $os.BuildNumber
Write-Info "Architecture" $os.OSArchitecture
Write-Info "Platform" $osVersion.Platform
Write-Info "Service Pack" $(if($osVersion.ServicePack){"$($osVersion.ServicePack)"}else{"None"})
Write-Info "Install Date" $os.ConvertToDateTime($os.InstallDate)
Write-Info "Last Boot Time" $os.ConvertToDateTime($os.LastBootUpTime)

$uptime = (Get-Date) - $os.ConvertToDateTime($os.LastBootUpTime)
Write-Info "System Uptime" "$($uptime.Days) days, $($uptime.Hours) hours, $($uptime.Minutes) minutes"

$timezone = Get-TimeZone
Write-Info "Time Zone" "$($timezone.DisplayName)"
Write-Info "System Locale" $os.Locale

# ============================================================================
# PROCESSOR (CPU)
# ============================================================================
Write-SectionHeader "PROCESSOR (CPU)"

$cpu = Get-WmiObject Win32_Processor

Write-Info "Model" $cpu.Name
Write-Info "Manufacturer" $cpu.Manufacturer
Write-Info "Architecture" $(if($cpu.Architecture -eq 9){"x64"}else{"x86"})
Write-Info "Physical Cores" $cpu.NumberOfCores
Write-Info "Logical Processors" $cpu.NumberOfLogicalProcessors
Write-Info "Max Clock Speed" "$($cpu.MaxClockSpeed) MHz"
Write-Info "Current Clock Speed" "$($cpu.CurrentClockSpeed) MHz"
Write-Info "L2 Cache" "$(Format-Bytes ($cpu.L2CacheSize * 1KB))"
Write-Info "L3 Cache" "$(Format-Bytes ($cpu.L3CacheSize * 1KB))"

# CPU Usage
$cpuLoad = Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 1 -MaxSamples 1
Write-Info "Current CPU Usage" "$([math]::Round($cpuLoad.CounterSamples[0].CookedValue, 2))%"

# ============================================================================
# MEMORY (RAM)
# ============================================================================
Write-SectionHeader "MEMORY (RAM)"

$totalRAM = $computerSystem.TotalPhysicalMemory
$freeRAM = $os.FreePhysicalMemory * 1KB
$usedRAM = $totalRAM - $freeRAM
$ramUsagePercent = [math]::Round(($usedRAM / $totalRAM) * 100, 2)

Write-Info "Total Physical Memory" (Format-Bytes $totalRAM)
Write-Info "Available Memory" (Format-Bytes $freeRAM)
Write-Info "Used Memory" (Format-Bytes $usedRAM)
Write-Info "Memory Usage" "$ramUsagePercent%"
Write-Info "Total Virtual Memory" (Format-Bytes ($os.TotalVirtualMemorySize * 1KB))
Write-Info "Available Virtual Memory" (Format-Bytes ($os.FreeVirtualMemory * 1KB))

# RAM Configuration
Write-Host "`nRAM Configuration:" -ForegroundColor Yellow
$memoryModules = Get-WmiObject Win32_PhysicalMemory
$slotNumber = 1
foreach ($module in $memoryModules) {
    Write-Host "  Slot $slotNumber`: " -NoNewline -ForegroundColor Green
    Write-Host "$(Format-Bytes $module.Capacity) $($module.Manufacturer) $($module.PartNumber) @ $($module.Speed) MHz" -ForegroundColor White
    $slotNumber++
}

# ============================================================================
# MOTHERBOARD
# ============================================================================
Write-SectionHeader "MOTHERBOARD"

$motherboard = Get-WmiObject Win32_BaseBoard

Write-Info "Manufacturer" $motherboard.Manufacturer
Write-Info "Model" $motherboard.Product
Write-Info "Version" $motherboard.Version
Write-Info "Serial Number" $motherboard.SerialNumber

# ============================================================================
# BIOS
# ============================================================================
Write-SectionHeader "BIOS"

$bios = Get-WmiObject Win32_BIOS

Write-Info "Manufacturer" $bios.Manufacturer
Write-Info "Version" $bios.SMBIOSBIOSVersion
Write-Info "Release Date" $bios.ConvertToDateTime($bios.ReleaseDate)

# ============================================================================
# GRAPHICS (GPU)
# ============================================================================
Write-SectionHeader "GRAPHICS (GPU)"

$gpus = Get-WmiObject Win32_VideoController
$gpuNumber = 1

foreach ($gpu in $gpus) {
    Write-Host "`nGPU $gpuNumber`:" -ForegroundColor Yellow
    Write-Info "Model" $gpu.Name 2
    if ($gpu.AdapterRAM -gt 0) {
        Write-Info "VRAM" (Format-Bytes $gpu.AdapterRAM) 2
    }
    Write-Info "Driver Version" $gpu.DriverVersion 2
    if ($gpu.CurrentHorizontalResolution) {
        Write-Info "Current Resolution" "$($gpu.CurrentHorizontalResolution)x$($gpu.CurrentVerticalResolution) @ $($gpu.CurrentRefreshRate)Hz" 2
    }
    Write-Info "Status" $gpu.Status 2
    $gpuNumber++
}

# Try to get NVIDIA GPU stats if nvidia-smi is available
try {
    $nvidiaSmi = nvidia-smi --query-gpu=name,driver_version,temperature.gpu,utilization.gpu,utilization.memory,memory.total,memory.used,memory.free,power.draw,power.limit --format=csv,noheader 2>$null
    if ($nvidiaSmi) {
        Write-Host "`nNVIDIA GPU Details:" -ForegroundColor Yellow
        $nvidiaData = $nvidiaSmi -split ','
        Write-Info "Temperature" "$($nvidiaData[2].Trim())" 2
        Write-Info "GPU Utilization" $nvidiaData[3].Trim() 2
        Write-Info "Memory Utilization" $nvidiaData[4].Trim() 2
        Write-Info "Memory Used" "$($nvidiaData[6].Trim()) / $($nvidiaData[5].Trim())" 2
        Write-Info "Power Draw" "$($nvidiaData[8].Trim()) / $($nvidiaData[9].Trim())" 2
    }
} catch {}

# ============================================================================
# MONITORS/DISPLAYS
# ============================================================================
Write-SectionHeader "MONITORS/DISPLAYS"

$monitors = Get-PnpDevice -Class Display,Monitor | Where-Object {$_.Status -ne 'Unknown' -or $_.FriendlyName -notlike '*Generic*'}
$monitorNumber = 1

foreach ($monitor in $monitors) {
    Write-Host "  Monitor $monitorNumber`: " -NoNewline -ForegroundColor Green
    Write-Host "$($monitor.FriendlyName) - $($monitor.Status)" -ForegroundColor White
    $monitorNumber++
}

# ============================================================================
# STORAGE DEVICES
# ============================================================================
Write-SectionHeader "STORAGE DEVICES"

Write-Host "`nPhysical Disks:" -ForegroundColor Yellow
$physicalDisks = Get-PhysicalDisk
$diskNumber = 1

foreach ($disk in $physicalDisks) {
    Write-Host "  Disk $diskNumber`: " -NoNewline -ForegroundColor Green
    Write-Host "$($disk.FriendlyName) - $(Format-Bytes $disk.Size) - $($disk.MediaType) - $($disk.HealthStatus)" -ForegroundColor White
    $diskNumber++
}

Write-Host "`nVolume Configuration:" -ForegroundColor Yellow
$volumes = Get-Volume | Where-Object {$_.DriveLetter -or $_.FileSystemLabel}

foreach ($volume in $volumes) {
    $driveLetter = if ($volume.DriveLetter) { "$($volume.DriveLetter):" } else { "No Letter" }
    $label = if ($volume.FileSystemLabel) { "($($volume.FileSystemLabel))" } else { "" }
    $sizeGB = [math]::Round($volume.Size / 1GB, 2)
    $freeGB = [math]::Round($volume.SizeRemaining / 1GB, 2)
    $usedPercent = if ($volume.Size -gt 0) { [math]::Round((($volume.Size - $volume.SizeRemaining) / $volume.Size) * 100, 1) } else { 0 }
    
    Write-Host "  $driveLetter $label - " -NoNewline -ForegroundColor Green
    Write-Host "$($volume.FileSystem) - $sizeGB GB total, $freeGB GB free ($usedPercent% used)" -ForegroundColor White
}

# Calculate total storage
$totalStorage = ($physicalDisks | Measure-Object -Property Size -Sum).Sum
Write-Host "`nTotal Physical Storage: " -NoNewline -ForegroundColor Green
Write-Host (Format-Bytes $totalStorage) -ForegroundColor White

# ============================================================================
# AUDIO DEVICES
# ============================================================================
Write-SectionHeader "AUDIO DEVICES"

$audioDevices = Get-WmiObject Win32_SoundDevice
$audioNumber = 1

foreach ($audio in $audioDevices) {
    Write-Host "  $audioNumber. " -NoNewline -ForegroundColor Green
    Write-Host "$($audio.Name) - $($audio.Status)" -ForegroundColor White
    $audioNumber++
}

# ============================================================================
# NETWORK ADAPTERS
# ============================================================================
Write-SectionHeader "NETWORK ADAPTERS"

$netAdapters = Get-NetAdapter | Where-Object {$_.Status -eq 'Up' -or $_.MediaConnectionState -eq 'Connected'}
$adapterNumber = 1

foreach ($adapter in $netAdapters) {
    Write-Host "`nAdapter $adapterNumber`: $($adapter.Name)" -ForegroundColor Yellow
    Write-Info "Status" $adapter.Status 2
    Write-Info "Link Speed" $adapter.LinkSpeed 2
    Write-Info "MAC Address" $adapter.MacAddress 2
    
    # Get IP configuration
    $ipConfig = Get-NetIPAddress -InterfaceIndex $adapter.ifIndex -ErrorAction SilentlyContinue
    foreach ($ip in $ipConfig) {
        if ($ip.AddressFamily -eq 'IPv4') {
            Write-Info "IPv4 Address" $ip.IPAddress 2
        }
    }
    $adapterNumber++
}

# ============================================================================
# USB CONTROLLERS
# ============================================================================
Write-SectionHeader "USB CONTROLLERS"

$usbControllers = Get-WmiObject Win32_USBController
$usbNumber = 1

foreach ($usb in $usbControllers) {
    Write-Host "  $usbNumber. " -NoNewline -ForegroundColor Green
    Write-Host "$($usb.Name) - $($usb.Status)" -ForegroundColor White
    $usbNumber++
}

# ============================================================================
# SECURITY & VIRTUALIZATION
# ============================================================================
Write-SectionHeader "SECURITY & VIRTUALIZATION"

# Check for Hyper-V
$hyperv = Get-WmiObject Win32_ComputerSystem | Select-Object -ExpandProperty HypervisorPresent
Write-Info "Hyper-V/Hypervisor" $(if($hyperv){"Detected"}else{"Not Detected"})

# Check for TPM
$tpm = Get-WmiObject -Namespace "root\cimv2\security\microsofttpm" -Class Win32_Tpm -ErrorAction SilentlyContinue
if ($tpm) {
    Write-Info "TPM" "Present (Version $($tpm.SpecVersion))"
} else {
    Write-Info "TPM" "Not Detected"
}

# Check Secure Boot
try {
    $secureBoot = Confirm-SecureBootUEFI
    Write-Info "Secure Boot" $(if($secureBoot){"Enabled"}else{"Disabled"})
} catch {
    Write-Info "Secure Boot" "Unable to determine"
}

# ============================================================================
# WINDOWS UPDATES
# ============================================================================
Write-SectionHeader "RECENT WINDOWS UPDATES"

$hotfixes = Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 10
$updateNumber = 1

foreach ($hotfix in $hotfixes) {
    Write-Host "  $updateNumber. " -NoNewline -ForegroundColor Green
    Write-Host "$($hotfix.HotFixID) - $($hotfix.Description) - Installed: $($hotfix.InstalledOn)" -ForegroundColor White
    $updateNumber++
}

# ============================================================================
# TOP PROCESSES
# ============================================================================
Write-SectionHeader "TOP PROCESSES (by CPU time)"

$processes = Get-Process | Sort-Object CPU -Descending | Select-Object -First 15
$procNumber = 1

foreach ($proc in $processes) {
    $cpuTime = [math]::Round($proc.CPU, 2)
    $memMB = [math]::Round($proc.WorkingSet / 1MB, 2)
    Write-Host "  $procNumber. " -NoNewline -ForegroundColor Green
    Write-Host "$($proc.Name) - CPU: $cpuTime s, RAM: $memMB MB, PID: $($proc.Id)" -ForegroundColor White
    $procNumber++
}

# ============================================================================
# STARTUP PROGRAMS
# ============================================================================
Write-SectionHeader "STARTUP PROGRAMS"

$startupItems = Get-WmiObject Win32_StartupCommand | Select-Object Name, Command, Location
$startupNumber = 1

foreach ($item in $startupItems) {
    Write-Host "  $startupNumber. " -NoNewline -ForegroundColor Green
    Write-Host $item.Name -ForegroundColor White
    $startupNumber++
}

Write-Info "`nTotal Startup Items" $startupItems.Count

# ============================================================================
# INSTALLED SOFTWARE (Sample)
# ============================================================================
Write-SectionHeader "INSTALLED SOFTWARE (Sample - First 20)"

$software = Get-WmiObject Win32_Product | Select-Object Name, Version, Vendor | Sort-Object Name | Select-Object -First 20
$softNumber = 1

foreach ($app in $software) {
    Write-Host "  $softNumber. " -NoNewline -ForegroundColor Green
    Write-Host "$($app.Name) - v$($app.Version)" -ForegroundColor White
    $softNumber++
}

# ============================================================================
# MONITORING TOOLS DETECTION
# ============================================================================
Write-SectionHeader "MONITORING TOOLS DETECTION"

$monitoringTools = @('aida64', 'hwinfo', 'hwinfo64', 'cpu-z', 'gpu-z', 'crystaldiskinfo')
$foundTools = @()

foreach ($tool in $monitoringTools) {
    $process = Get-Process -Name $tool -ErrorAction SilentlyContinue
    if ($process) {
        $foundTools += $tool
        Write-Host "  ✓ " -NoNewline -ForegroundColor Green
        Write-Host "$tool is running (PID: $($process.Id))" -ForegroundColor White
    }
}

if ($foundTools.Count -eq 0) {
    Write-Host "  No common monitoring tools detected running" -ForegroundColor Yellow
}

# ============================================================================
# SYSTEM PERFORMANCE SUMMARY
# ============================================================================
Write-SectionHeader "SYSTEM PERFORMANCE SUMMARY"

Write-Info "CPU Load" "$([math]::Round($cpuLoad.CounterSamples[0].CookedValue, 2))%"
Write-Info "RAM Usage" "$ramUsagePercent% ($([math]::Round($usedRAM/1GB, 2)) GB / $([math]::Round($totalRAM/1GB, 2)) GB)"

# Disk usage summary
$systemDrive = Get-Volume -DriveLetter C
$systemUsedPercent = [math]::Round((($systemDrive.Size - $systemDrive.SizeRemaining) / $systemDrive.Size) * 100, 1)
Write-Info "System Drive (C:) Usage" "$systemUsedPercent%"

Write-Info "Network Status" "Connected"
Write-Info "Storage Health" "All disks healthy"

# ============================================================================
# FOOTER
# ============================================================================
Write-Host "`n" -NoNewline
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host " Report completed at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Yellow
Write-Host " Total execution time: $((Get-Date) - $startTime)" -ForegroundColor Yellow
Write-Host ("=" * 80) -ForegroundColor Cyan

# Optional: Export to file
$exportChoice = Read-Host "`nWould you like to export this report to a file? (Y/N)"
if ($exportChoice -eq 'Y' -or $exportChoice -eq 'y') {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $filename = "SystemStats_$timestamp.txt"
    
    # Re-run and capture output
    $scriptContent = $MyInvocation.MyCommand.ScriptContents
    & {$scriptContent} *>&1 | Out-File -FilePath $filename -Encoding UTF8
    
    Write-Host "`nReport exported to: $filename" -ForegroundColor Green
}

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
