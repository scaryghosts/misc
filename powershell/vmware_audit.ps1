if ( !(Get-Pssnapin -name VMware.VimAutomation.Core -erroraction silentlycontinue) ) 
	{ 
		add-pssnapin VMware.VimAutomation.Core
		
	 }



function send-mailalert([string]$msgtext) {

	$smtpserver = "smtp.mailtown.com"
	$msg = new-object net.mail.mailmessage
	$smtp = new-object net.mail.smtpclient($smtpserver)
	$msg.from = "vmwareaudit@grasshopper.net"
	$msg.to.add("slithesnake@snakes.hill")
	$msg.to.add("billythekid@rooster.net")
	$msg.to.add("zigtothezag@zog.com")
	$msg.to.add("troggs@home.bet")
	#$msg.to.add("alert@mail.zoo.com")
	$msg.subject = "VMWARE AUDIT: prod-vc"
	$msg.body = $msgtext

	$smtp.send($msg)

	

	

}

	
	 

	 
connect-viserver vcenter

$prodvc= @{}

$allvms = get-vm
$old_prodvc = import-clixml -path c:\vmware\vc_list.xml
$body = ''


foreach ($vm in $allvms) {
	
	$name = $vm.name
	$numcpu = $vm.numcpu
	$memory = $vm.memorygb
	$storage = ($vm | get-harddisk | Measure-Object capacitygb -sum).sum

	
	if ($name -eq "template1.fq.dn" -or $name -eq "template2.fq.dn" -or $name -eq "wasps.template.01") { continue }
	
	$holder = New-Object PSobject -property @{
		Name = $name
		Numcpu = $numcpu
		MemoryGB = $memory
		Storage = $storage
	}
	
	$prodvc[$name] = $holder
	
	if ($old_prodvc.keys -notcontains $name) {
		$body += "NEW VM: $name`n"
		
		try {
			$event = $vm | Get-VIEvent -Start (get-date).addhours(-3) -Finish (get-date) | ? {$_.fullformattedmessage -like "Deploying *" -or $_.fullformattedmessage -like "Creating *"}
			$username = $event.username
			$message = $event.fullformattedmessage
			
			$body += "	Deployed by: $username`n"
			$body += "	Stats: $numcpu vcpu / $memory GB memory / $storage GB storage `n"
			$body += "	Message: $message`n"
		}
		catch {
			$body += "	ERROR: Could not parse events`n"
		}
		continue
	}
	
	$oldvm = $old_prodvc[$name]
	$oldnumcpu = $oldvm.Numcpu
	$oldmemory = $oldvm.MemoryGB
	$oldstorage = $oldvm.Storage
	
	
	if ($numcpu -ne $oldnumcpu) {
		$body += "CHANGE: $name changed CPU count from $oldnumcpu to $numcpu `n`n"
		
		
	}
	
	if ($memory -ne $oldmemory) {
		$body += "CHANGE: $name changed memory from $oldmemory GB to $memory GB `n`n"
	}
	
	if ($storage -ne $oldstorage) {
		$body += "CHANGE: $name changed storage from $oldstorage GB to $storage GB `n`n"
	}
	
	
	
	
	
	
	
}


foreach ($oldkey in $old_prodvc.keys) {
	if ($prodvc.keys -notcontains $oldkey) {
		$body += "REMOVAL: $oldkey `n"
	}
}


if ($body) {
	write-output "$body" | out-file c:\vmware\test.txt
	send-mailalert $body
}



disconnect-viserver * -confirm:$false

$prodvc | export-clixml -path c:\vmware\vc_list.xml -confirm:$false -force
