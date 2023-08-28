# Vault-fix

vault-fix is a CLI utility and python package that helps exporting and importing secrets to and from [Vault] instances.
You can use this either to load fixture files for local development (it's original purpose). Or to migrate data from
Vault instance to another, while secrets may be [encrypted](#Encrypting-output) and/or
[piped to another vault-fix instance](#Directing-data-to-the-load-command) so the data is not persisted.

## Historical context

vault-fix was created to address an issue with the default mode of [Vault instances in dev mode], for local development.
Vault will start with ephemeral storage, i.e. in-memory, mounting a volume will not make it persistent. If you want to
have persistent data, you'd have to provision a mount and a volume. However, this will make your local test environment
more stateful, which is not always desirable. Plus a normal Vault instance will can "seal" itself to protect itself
from attackers, which is not something you normally want to deal with during development.

Instead you may want to load a known fixture, containing a curated set of secrets that you don't want to manually set
every time you restarted vault. In other words, a fixture. This allows you to start from a clean slate every time you
test or debug. You can [automate the loading](#Using-vault-fix-as-a-Python-package) or dumping of secrets, and/or use
the CLI.

## Installation

```bash
pip install vault-fix
```

## Usage

Finding out how this works:

```bash
vault-fix --help

 Usage: vault-fix [OPTIONS] COMMAND [ARGS]...

 Load or dump data?

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                         │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.  │
│ --help                        Show this message and exit.                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ dump         Load up, and dump secrets to and from Vault.                                                       │
│ load         Load up, and dump secrets to and from Vault.                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Specific to dumping fixtures:

```bash
vault-fix dump --help

 Usage: vault-fix dump [OPTIONS] MOUNT PATH

 Load up, and dump secrets to and from Vault.

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    mount      TEXT  Vault mount [default: None] [required]                                                    │
│ *    path       TEXT  Vault path within the mount [default: None] [required]                                    │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --token       -t                 TEXT         Vault access token. [default: None] [required]                 │
│    --host        -H                 TEXT         Vault hostname [default: localhost]                            │
│    --port        -P                 INTEGER      Vault network port. [default: 8200]                            │
│    --tls             --no-tls                    Enable or disable TLS [default: tls]                           │
│    --verbose     -v                 INTEGER      Specify verbosity level by passing more 1 or more -v -vv       │
│                                                  -vvv's                                                         │
│                                                  [default: 0]                                                   │
│    --file        -f                 TEXT         Output file, stdout if not specified [default: -]              │
│    --password    -p                 TEXT         Password to encrypt the dumped fixture, or none for plain text │
│                                                  output.                                                        │
│    --pretty          --no-pretty                 Pretty print the output (if JSON formatted [default: pretty]   │
│    --serializer                     [json|yaml]  Which serializer do you prefer? [default=yaml] [default: yaml] │
│    --help                                        Show this message and exit.                                    │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Specific to loading fixtures:

```bash
vault-fix load --help

 Usage: vault-fix load [OPTIONS] MOUNT PATH

 Load up, and dump secrets to and from Vault.

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    mount      TEXT  Vault mount [default: None] [required]                                                    │
│ *    path       TEXT  Vault path within the mount [default: None] [required]                                    │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --token         -t              TEXT              Vault access token. [default: None] [required]             │
│    --host          -H              TEXT              Vault hostname [default: localhost]                        │
│    --port          -P              INTEGER           Vault network port. [default: 8200]                        │
│    --tls               --no-tls                      Enable or disable TLS [default: tls]                       │
│    --verbose       -v              INTEGER           Specify verbosity level by passing more 1 or more -v -vv   │
│                                                      -vvv's                                                     │
│                                                      [default: 0]                                               │
│    --file          -f              TEXT              Input file, assumes stdin if not specified [default: -]    │
│    --password      -p              TEXT              Password to decrypt the dumped fixture, or none for plain  │
│                                                      text input.                                                │
│    --deserializer                  [json|yaml|auto]  Which deserializer does the fixture file require?          │
│                                                      [default: auto]                                            │
│    --help                                            Show this message and exit.                                │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Examples

### Simple dump

Dump secrets from a locally running vault instance:

```bash
vault-fix dump secret / --no-tls
```

### Directing output

Output will be printed to stdout, you can specify `-f FILE` or direct output to a file, like:

```bash
vault-fix dump secret / --no-tls > my-fixture.yaml
```

### Encrypting output

If you want your secrets encrypted, pass `-p` to get a password prompt, or pass the password on the command line (not safe).

```bash
vault-fix dump secret / --no-tls -p
```

Only secrets will be encrypted, the paths will be in plain text.

### JSON instead of YAML

If you want your secrets dumped in JSON format instead of the default YAML format, pass `--serializer json`

```bash
vault-fix dump secret / --no-tls --serializer json
```

### Simple load

Load secrets from a file to a locally running vault instance:

```bash
vault-fix load secret / --no-tls -f my-fixture.json
```

If the fixture is encrypted, you need to pass the `-p` parameter, or you will get a runtime error.

### Directing data to the load command

Load secrets from a file to a locally running vault instance:

```bash
cat my-fixture.json | vault-fix load secret / --no-tls --deserializer json
```

Which brings us to this command, that allow you to migrate secrets between vault instances:

```bash
vault-fix dump secret / -H vault.dev.yourdomain.com | vault-fix load secret / --no-tls
```

## Using vault-fix as a Python package

One of the best things about this utility is that you can automatically load fixtures to a local vault dev server, e.g.
during application startup.

```python
from hvac import Client
from vault_fix.load import load_fixture_from_file
from vault_fix.serializers.yaml import yaml_deserializer

# Vault docker container running on your local machine in dev mode, with ephemeral storage.
# Assuming the following defaults
VAULT_ADDR = "http://vault:8200"
VAULT_TOKEN = "root"
VAULT_TLS_ENABLED = False
VAULT_MOUNT = "secret"
FIXTURE_PATH = "../vault_fixture_local_dev.yaml"

def load_vault_secrets() -> None:
    print(f"Attempting to import vault fixture from {FIXTURE_PATH}")
    client = Client(url=VAULT_ADDR, token=VAULT_TOKEN, verify=VAULT_TLS_ENABLED)
    try:
        with open(FIXTURE_PATH, "rt") as fixture_fh:
            load_fixture_from_file(
                hvac=client, fixture=fixture_fh, mount_point=VAULT_MOUNT, deserializer=yaml_deserializer
            )
        print(f"Imported vault fixture from {FIXTURE_PATH}")
    except OSError:
        print(f"Can't read fixture file from {FIXTURE_PATH}")
```

### Other good to knows

- The path parameter specifies the path in the vault server you want to dump.
  Or the path you would like to load to a server from the fixture file. Meaning you can select a subset of secrets to
  dump or load from servers or fixtures respectively.
- vault-fix does not dump or import metadata, including previous versions of secrets.

## Hacking on this utility

Checkout the project, make a virtual env with hatch and install dependencies.

```bash
git checkout git@github.com:SnijderC/vault-fix.git
cd vault-fix
pre-commit install
pip install hatch
hatch shell
```

### Running tests

If you're in a hatch shell, exit it first, then:

```bash
hatch run test:pytest
```

This will test vault-fix against Python 3.9 - 3.11. If you don't have all of those, they will be skipped. You can
install them with [pyenv](https://github.com/pyenv/pyenv#installation):

```bash
pyenv install 3.9 3.10 3.11
```

[Vault]: https://www.vaultproject.io/
[Vault instances in dev mode]: https://developer.hashicorp.com/vault/tutorials/getting-started/getting-started-dev-server#starting-the-dev-server
