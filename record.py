import argparse
import getpass
import json
import math
import pathlib
import random
import typing
import urllib.parse
import urllib.request

SOFTWARE_NAME = pathlib.Path(__file__).stem
__version__ = "0.0.1"
USER_AGENT = f"{SOFTWARE_NAME}/{__version__}"


class RPCException(Exception):
    def __init__(self, message, traceback):
        super().__init__()
        self.message = message
        self.traceback = traceback

    def __str__(self):
        return "\n".join((self.message, "", self.traceback))


def jsonrpc_params(
    params, call_id: typing.Optional[int] = None
) -> typing.Dict[str, typing.Any]:
    if call_id is None:
        call_id = int(math.floor(random.random() * 1e9))
    return {
        "jsonrpc": "2.0",
        "method": "call",
        "params": params,
        "id": call_id,
    }


def unwrap_rpc_result(response) -> typing.Any:
    response_json = json.loads(response.read())
    error = response_json.get("error")
    if error:
        message = error.get("message") or "Odoo Server Error"
        data = error.get("data") or {}
        traceback = data.get("debug") or ""
        raise RPCException(message, traceback)
    return response_json.get("result")


def call_json_rpc(
    url: str,
    service: str,
    method: str,
    args: typing.List[typing.Any],
    timeout: typing.Optional[float] = None,
    encoding: str = "utf-8",
):
    json_data = jsonrpc_params(
        {
            "service": service,
            "method": method,
            "args": args,
        }
    )

    request = urllib.request.Request(
        urllib.parse.urljoin(url, "jsonrpc"),
        data=json.dumps(json_data).encode(encoding),
        headers={
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
    )
    return urllib.request.urlopen(request, timeout=timeout)


parser = argparse.ArgumentParser(prog=SOFTWARE_NAME)
parser.add_argument(
    "--version",
    action="version",
    version=f"%(prog)s {__version__}",
    help="print program version",
)
parser.add_argument("url", help="URL to Odoo instance")
parser.add_argument("db", help="Odoo database name")
parser.add_argument("model", help="record model name")
parser.add_argument("--timeout", type=float, default=60)
parser.add_argument(
    "ids", help="database IDs of the records", type=int, nargs="+", metavar="id"
)
parser.add_argument(
    "-u",
    "--username",
    default="admin",
    help="login of the Odoo user to use",
    dest="login",
)
parser.add_argument(
    "-w",
    "--password",
    help="Odoo user's password. If not specified, you will be asked when starting",
    dest="pw",
    metavar="PASSWORD",
)
parser.add_argument(
    "--lang",
    default="en_US",
    help="language code, will be used in the context. Default: %(default)s",
)

cli_args = parser.parse_args()

url, db, login, pw, model, ids, timeout = (
    cli_args.url,
    cli_args.db,
    cli_args.login,
    cli_args.pw,
    cli_args.model,
    cli_args.ids,
    cli_args.timeout,
)
if not pw:
    pw = getpass.getpass(f"Please enter the password of '{login}' Odoo user: ")

context = {
    "lang": cli_args.lang,
}

uid = unwrap_rpc_result(
    call_json_rpc(url, "common", "login", [db, login, pw], timeout=timeout)
)

if not uid:
    print("Invalid login/password")


def execute_kw(model: str, method: str, *args, **kwargs):
    return unwrap_rpc_result(
        call_json_rpc(
            url,
            "object",
            "execute_kw",
            [db, uid, pw, model, method, args, kwargs],
            timeout=timeout,
        )
    )


def read(fields: typing.Optional[typing.List[str]] = None):
    return execute_kw(model, "read", ids, fields or [], context=context)


def write(vals: typing.Dict[str, typing.Any]):
    return execute_kw(model, "write", ids, vals, context=context)
