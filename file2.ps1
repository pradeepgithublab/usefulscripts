# Function to enable a specific add-in by name in Word
function Enable-SpecificAddinInWord {
    try {
        $word = New-Object -ComObject Word.Application
        $word.Visible = $true
        $addIns = $word.COMAddIns
        foreach ($addIn in $addIns) {
            if ($addIn.Description -eq "Scout") {
                $addIn.Connect = $true  # Enable the specific add-in
                Write-Output "Enabled Word Add-in: $($addIn.Description)"
            }
        }
    } catch {
        Write-Error "Error enabling Scout add-in in Word: $_"
    } finally {
        if ($word -is [__ComObject]) { $word.Quit() }
    }
}

# Function to enable a specific add-in by name in Excel
function Enable-SpecificAddinInExcel {
    try {
        $excel = New-Object -ComObject Excel.Application
        $excel.Visible = $true
        $addIns = $excel.COMAddIns
        foreach ($addIn in $addIns) {
            if ($addIn.Description -eq "Scout") {
                $addIn.Connect = $true  # Enable the specific add-in
                Write-Output "Enabled Excel Add-in: $($addIn.Description)"
            }
        }
    } catch {
        Write-Error "Error enabling Scout add-in in Excel: $_"
    } finally {
        if ($excel -is [__ComObject]) { $excel.Quit() }
    }
}

# Function to enable a specific add-in by name in PowerPoint
function Enable-SpecificAddinInPowerPoint {
    try {
        $powerpoint = New-Object -ComObject PowerPoint.Application
        $powerpoint.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue
        $addIns = $powerpoint.COMAddIns
        foreach ($addIn in $addIns) {
            if ($addIn.Description -eq "Scout") {
                $addIn.Connect = $true  # Enable the specific add-in
                Write-Output "Enabled PowerPoint Add-in: $($addIn.Description)"
            }
        }
    } catch {
        Write-Error "Error enabling Scout add-in in PowerPoint: $_"
    } finally {
        if ($powerpoint -is [__ComObject]) { $powerpoint.Quit() }
    }
}

# Activate the "Scout" add-in in Word, Excel, and PowerPoint
Enable-SpecificAddinInWord
Enable-SpecificAddinInExcel
Enable-SpecificAddinInPowerPoint
