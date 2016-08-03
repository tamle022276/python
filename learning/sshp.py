import paramiko
import sys
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.load_system_host_keys()
ssh.connect(hostname='helacop1', username='root', password='Sit4me123!')
print (ssh)
#command = '/usr/pde/bin/cnsrun -utility filer -commands "{enable script} {scandisk} {yes} {quit} " -debug 3 -force'
command = '/usr/pde/bin/cnsrun -utility checktableb -prompt "Enter a command, \\"QUIT;\\" or \\"HELP;\\"" -commands "{check all tables at level two;} {quit;} " -debug 5 -force'
stdin, stdout, stderr = ssh.exec_command(command)
# block until remote command completes
status = stdout.channel.recv_exit_status()
# status 0 completed passed, non0 completed failed
print (status)
#http://stackoverflow.com/questions/10019456/usage-of-sys-stdout-flush-method
sys.stdout.flush()

with open('check.log','wb') as the_file:
    for line in stdout.read().splitlines():
        the_file.write(line + "\n".encode('ascii'))
