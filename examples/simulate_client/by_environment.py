import os
os.environ['FLASK_NATIVE_RUNNING_MODE'] = 'client'
os.environ['FLASK_NATIVE_HOST'] = 'localhost'
os.environ['FLASK_NATIVE_PORT'] = '2000'

from examples.simulate_client.in_script import hello
print(hello('world'))

# proc 1: py examples/simulate_client/in_script.py server
# proc 2: py examples/simulate_client/by_environment.py
