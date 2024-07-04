# `cflr` a Cloudflare Admin CLI

A collection of commands for working with a Cloudflare account.

This package authenticates against the [Cloudflare API](https://developers.cloudflare.com/api/) using environment variables. For managing these securely consider the excellent [cf-vault](https://github.com/jacobbednarz/cf-vault) project.

## Quickstart

:warning: Python `>=3.11.x` required.

```sh
$ git clone
$ python -m venv .venv
$ source .venv/bin/activate # DO NOT SKIP THIS STEP!
# install dependencies (pyproject.toml)
# if developing run `python -m pip install -e ".[dev]"` for an editable install
$ python -m pip install .
# run cflr
$ cflr --help
# or
$ python -m cflr --help
# or
$ python cflr/cli.py --help
```

## Commands

### `$ sso`

- **Enterprise** only.
- API endpoint: `/accounts/:account_id/sso/v2/connectors` (undocumented as of 2024-01-13)
  - Requires [Global API Key](https://developers.cloudflare.com/fundamentals/api/get-started/keys/) environment variables to be set.

`list`/`enable`/`disable` the SSO email domains configured.

#### Why is this useful

Cloudflare allow Enterprise plans to configure IdP's to [enforce SSO access to the dashboard](https://developers.cloudflare.com/cloudflare-one/applications/configure-apps/dash-sso-apps/) across email domain(s).

:warning: If the IdP were to suffer an outage, access to the Cloudflare dashboard would be impacted as the SSO flow would fail.

In this instance, **disabling** the associated SSO email domain(s) will allow users to fallback to logging in via username/password/2FA.

#### Usage

```sh
$ cflr sso --help
$ cflr sso list :account_id
$ cflr sso disable :account_id  # an interactive pick list is returned
$ cflr sso enable :account_id   # an interactive pick list is returned
```
