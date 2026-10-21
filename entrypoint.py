import sys
import subprocess

# GitHub Actions passes inputs as arguments based on action.yml
spec = sys.argv[1]
output = sys.argv[2]
validate = sys.argv[3].lower() == 'true'

if validate:
    # If validate is true, we run validation first.
    # If it fails, we exit and fail the action.
    validate_cmd = ['python', 'api2md.py', '--spec', spec, '--validate']
    result = subprocess.run(validate_cmd)
    if result.returncode != 0:
        print("Validation failed. Aborting generation.")
        sys.exit(1)

command = ['python', 'api2md.py', '--spec', spec, '--output', output]
subprocess.run(command, check=True)
