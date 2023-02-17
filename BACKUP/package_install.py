import sys
import subprocess

#package_list = ['lmfit']
#package_list = ['matplotlib','ntpath','datetime','pickle','pathlib','csv','copy','scipy','lmfit']
package_list = ['matplotlib','datetime','pathlib','scipy','lmfit']

subprocess.check_call(["python", "-m", "pip", "install", "--upgrade", "pip"])

# implement pip as a subprocess:
for element in package_list:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install',element])

# process output with an API in the subprocess module:
reqs = subprocess.check_output([sys.executable, '-m', 'pip',
'freeze'])
installed_packages = [r.decode().split('==')[0] for r in reqs.split()]

print(installed_packages)