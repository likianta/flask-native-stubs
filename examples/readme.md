# Run examples

Install all requirements:

```shell
# necessary deps for flask-native-stubs
pip install -r requirements.txt
# extra deps for all example scripts.
pip install -r requirements-dev.txt
```

Run a simple example:

```shell
# get help
py examples/simple_01/dry_run.py -h
#   py: use "python3"/"python"/"py".
#   examples/<...>/dry_run.py: every example has a "dry_run.py" to get start.
#   -h: show help message.

# then
py examples/simple_01/dry_run.py generate-stubs
py examples/simple_01/dry_run.py run-server
py examples/simple_01/dry_run.py test-client
py examples/simple_01/dry_run.py ...
```

# Example list

1.  simple_01

    A very basic example demonstrates how it works.

2.  simple_02

    A more realistic example.

3.  elegant_exit

    How does server raises an exception that could be catched by client.
