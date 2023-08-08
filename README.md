# Installation

```bash
pip install .
```

# Usage

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

### Other good to knows

- The path parameter specifies the path in the vault server you want to dump.
  Or the path you would like to load to a server from the fixture file. Meaning you can select a subset of secrets to
  dump or load from servers or fixtures respectively.
- vault-fix does not dump or import metadata, including previous versions of secrets.

# Hacking on this utility

```bash
python -m venv venv
source venv/bin/activate
pip install -e '.[dev]'
```
