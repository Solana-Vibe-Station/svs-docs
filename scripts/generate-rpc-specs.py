#!/usr/bin/env python3
"""
OpenAPI generator for the SVS Solana RPC and Historical RPC specs.

Emits one OpenAPI 3.0.3 path operation per JSON-RPC method so each method
renders as its own block in GitBook, instead of being collapsed into a single
"POST /" operation with method-specific examples.

The generated paths (e.g. /getBalance) are documentation-only groupings; the
actual production endpoint for every method is the root path of the chosen
SVS RPC server URL. Each operation's description states this explicitly.

Run from the repo root:
    python3 scripts/generate-rpc-specs.py

Outputs (overwrites):
    api-specs/solana-rpc.yaml
    api-specs/historical-rpc.yaml
"""

from __future__ import annotations

import os
import sys
import textwrap
from collections import OrderedDict

import yaml

# Local module — sibling file in the scripts/ folder.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import code_samples  # noqa: E402


# ---------------------------------------------------------------------------
# YAML emitter: keep dict ordering, multiline strings as block scalars.
# ---------------------------------------------------------------------------

class _OD(OrderedDict):
    pass


def _od_representer(dumper, data):
    return dumper.represent_mapping(
        "tag:yaml.org,2002:map", data.items(), flow_style=False
    )


def _str_representer(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.add_representer(_OD, _od_representer)
yaml.add_representer(str, _str_representer)


# ---------------------------------------------------------------------------
# Shared building blocks reused across both specs.
# ---------------------------------------------------------------------------

ENDPOINT_NOTE = textwrap.dedent(
    """\
    > **How to call this method**
    >
    > All Solana JSON-RPC requests POST to the **root path** (`/`) of the
    > chosen SVS RPC server. The path shown above (e.g. `/getBalance`) is a
    > documentation grouping — it lets each method render as its own
    > operation. The actual method dispatch happens via the `method` field
    > in the request body.
    """
)

HISTORICAL_ENDPOINT_NOTE = textwrap.dedent(
    """\
    > **How to call this method**
    >
    > Historical Solana RPC requests POST to **`/historical`** on the chosen
    > SVS server. The path shown above (e.g. `/historical/getBlock`) is a
    > documentation grouping — it lets each historical method render as its
    > own operation. The actual method dispatch happens via the `method`
    > field in the request body.
    """
)

SECURITY = [
    {},
    {"AuthHeader": []},
    {"URLParameter": []},
]

STANDARD_RESPONSES = _OD([
    ("401", _OD([("$ref", "#/components/responses/UnauthorizedError")])),
    ("403", _OD([("$ref", "#/components/responses/ForbiddenError")])),
    ("429", _OD([("$ref", "#/components/responses/TooManyRequestsError")])),
    ("500", _OD([("$ref", "#/components/responses/InternalServerError")])),
])


# ---------------------------------------------------------------------------
# Per-operation builders.
# ---------------------------------------------------------------------------

def _params_schema(params):
    if not params:
        return _OD([
            ("type", "array"),
            ("description", "No parameters."),
            ("maxItems", 0),
        ])
    # Each positional param gets its full schema (description, example,
    # nested properties for object params) inside `items: anyOf`. anyOf
    # (not oneOf) avoids strict validation errors when two adjacent
    # positional params share a primitive type.
    items_schemas = []
    for p in params:
        s = _OD()
        s["title"] = p["name"] + ("" if p.get("required") else " (optional)")
        for k, v in p["schema"].items():
            s[k] = v
        items_schemas.append(s)
    return _OD([
        ("type", "array"),
        ("description", "Positional parameters. Each item below corresponds to one position in the array, in order."),
        ("minItems", sum(1 for p in params if p.get("required"))),
        ("maxItems", len(params)),
        ("items", _OD([("anyOf", items_schemas)])),
    ])


def _request_body(method_name, params, example_params, extra_examples=None):
    """Build a requestBody with multiple named examples.

    The first example ("default") is built from `example_params`. Any
    `extra_examples` items (cap of 2) become additional named examples.
    GitBook renders these as a dropdown in the Test-It panel; the
    `default` key is the initially-selected one.
    """
    request_schema = _OD([
        ("type", "object"),
        ("required", ["jsonrpc", "id", "method", "params"]),
        ("properties", _OD([
            ("jsonrpc", _OD([
                ("type", "string"),
                ("enum", ["2.0"]),
                ("description", "JSON-RPC protocol version."),
                ("example", "2.0"),
            ])),
            ("id", _OD([
                ("oneOf", [
                    _OD([("type", "string")]),
                    _OD([("type", "integer")]),
                ]),
                ("description", "Request identifier echoed back in the response."),
                ("example", 1),
            ])),
            ("method", _OD([
                ("type", "string"),
                ("enum", [method_name]),
                ("description", f"Must be `{method_name}`."),
                ("example", method_name),
            ])),
            ("params", _params_schema(params)),
        ])),
    ])
    examples = _OD()
    examples["default"] = _OD([
        ("summary", "Standard request — required params only."),
        ("value", _OD([
            ("jsonrpc", "2.0"),
            ("id", 1),
            ("method", method_name),
            ("params", example_params),
        ])),
    ])
    for ex in (extra_examples or [])[:2]:
        examples[ex["name"]] = _OD([
            ("summary", ex["summary"]),
            ("value", _OD([
                ("jsonrpc", "2.0"),
                ("id", 1),
                ("method", method_name),
                ("params", ex["params"]),
            ])),
        ])
    return _OD([
        ("required", True),
        ("content", _OD([
            ("application/json", _OD([
                ("schema", request_schema),
                ("examples", examples),
            ])),
        ])),
    ])


def _success_response(method_name, result_schema, result_example):
    schema = _OD([
        ("allOf", [
            _OD([("$ref", "#/components/schemas/JsonRpcEnvelope")]),
            _OD([
                ("type", "object"),
                ("required", ["result"]),
                ("properties", _OD([("result", result_schema)])),
            ]),
        ]),
    ])
    return _OD([
        ("description", f"Successful `{method_name}` response."),
        ("content", _OD([
            ("application/json", _OD([
                ("schema", schema),
                ("example", _OD([
                    ("jsonrpc", "2.0"),
                    ("id", 1),
                    ("result", result_example),
                ])),
            ])),
        ])),
    ])


def build_operation(method, base_note=ENDPOINT_NOTE, historical=False, websocket=False):
    """Build a single OpenAPI Operation, including x-codeSamples and a
    multi-example requestBody.

    `historical=True` switches all code samples + curl URLs to the
    /historical path on the public endpoint."""
    name = method["name"]
    summary = f"{name} — {method['summary']}"
    description = method["description"].rstrip()
    if method.get("params"):
        description += "\n**Parameters**\n\n"
        for idx, p in enumerate(method["params"]):
            req = "required" if p.get("required") else "optional"
            description += f"{idx}. `{p['name']}` ({req}) — {p['schema_doc']}\n"

    extra_examples = code_samples.EXTRA_EXAMPLES.get(name, [])

    if historical:
        x_samples = code_samples.historical_code_samples_for(name, method["params_example"])
    elif websocket:
        x_samples = code_samples.websocket_code_samples_for(name, method["params_example"])
    else:
        x_samples = code_samples.code_samples_for(name, method["params_example"])

    op = _OD([
        ("operationId", name),
        ("summary", summary),
        ("tags", [method["tag"]]),
        ("description", description),
        ("requestBody", _request_body(name, method.get("params", []), method["params_example"], extra_examples)),
        ("responses", _OD([
            ("200", _success_response(name, method["result_schema"], method["result_example"])),
        ])),
        ("security", SECURITY),
        # Redocly / GitBook custom extension: language-specific code samples,
        # rendered as tabs above the "Test it" panel. cURL is the default tab.
        ("x-codeSamples", [
            _OD([("lang", s["lang"]), ("label", s["label"]), ("source", s["source"])])
            for s in x_samples
        ]),
    ])
    for code, body in STANDARD_RESPONSES.items():
        op["responses"][code] = body
    return op


def build_paths(methods, base_path_prefix="", base_note=ENDPOINT_NOTE, historical=False, websocket=False):
    """Build a paths map.

    `base_path_prefix` joins to the method name to form each path key.
    If the prefix ends with `#` (the historical case), no separator
    slash is inserted — the method name is appended directly to make
    a fragment-based path like `/historical#getBlock`. Otherwise we
    insert `/` so paths look like `/getBlock`.
    """
    paths = _OD()
    for m in methods:
        if base_path_prefix.endswith("#"):
            path = f"{base_path_prefix}{m['name']}"
        else:
            path = f"{base_path_prefix}/{m['name']}"
        paths[path] = _OD([("post", build_operation(m, base_note=base_note, historical=historical, websocket=websocket))])
    return paths


# ---------------------------------------------------------------------------
# Common shared schemas.
# ---------------------------------------------------------------------------

COMMON_COMPONENTS = _OD([
    ("schemas", _OD([
        ("JsonRpcEnvelope", _OD([
            ("type", "object"),
            ("required", ["jsonrpc", "id"]),
            ("description", "Base envelope of every JSON-RPC 2.0 response."),
            ("properties", _OD([
                ("jsonrpc", _OD([("type", "string"), ("enum", ["2.0"]), ("example", "2.0")])),
                ("id", _OD([
                    ("oneOf", [_OD([("type", "string")]), _OD([("type", "integer")])]),
                    ("description", "Echoed request id."),
                    ("example", 1),
                ])),
            ])),
        ])),
        ("JsonRpcErrorResponse", _OD([
            ("type", "object"),
            ("required", ["jsonrpc", "id", "error"]),
            ("description", "JSON-RPC 2.0 error response."),
            ("properties", _OD([
                ("jsonrpc", _OD([("type", "string"), ("enum", ["2.0"])])),
                ("id", _OD([("oneOf", [_OD([("type", "string")]), _OD([("type", "integer")])])])),
                ("error", _OD([("$ref", "#/components/schemas/JsonRpcError")])),
            ])),
        ])),
        ("JsonRpcError", _OD([
            ("type", "object"),
            ("required", ["code", "message"]),
            ("description", "Structured JSON-RPC error."),
            ("properties", _OD([
                ("code", _OD([
                    ("type", "integer"),
                    ("description",
                        "Numeric error code per JSON-RPC 2.0 spec. Common values:\n"
                        "- `-32700` Parse error\n"
                        "- `-32600` Invalid Request\n"
                        "- `-32601` Method not found\n"
                        "- `-32602` Invalid params\n"
                        "- `-32603` Internal error\n"
                        "- `-32003` Unauthorized\n"
                        "- `-32005` Too Many Requests\n"
                        "- `-32015` Transaction version not supported\n"),
                    ("example", -32602),
                ])),
                ("message", _OD([("type", "string"), ("example", "Invalid params")])),
                ("data", _OD([("type", "object"), ("additionalProperties", True)])),
            ])),
        ])),
        ("Context", _OD([
            ("type", "object"),
            ("description", "RPC context block returned alongside most account-level results."),
            ("required", ["slot"]),
            ("properties", _OD([
                ("slot", _OD([("type", "integer"), ("format", "int64"), ("example", 416997240)])),
                ("apiVersion", _OD([("type", "string"), ("example", "3.1.10")])),
            ])),
        ])),
        ("Commitment", _OD([
            ("type", "string"),
            ("enum", ["processed", "confirmed", "finalized"]),
            ("default", "finalized"),
            ("description",
                "How finalized a block is at query time:\n"
                "- `processed`: most recent block, may be skipped\n"
                "- `confirmed`: block confirmed by supermajority of cluster\n"
                "- `finalized`: block finalized by the cluster (>2/3 stake)"),
        ])),
        ("Encoding", _OD([
            ("type", "string"),
            ("enum", ["json", "jsonParsed", "base58", "base64", "base64+zstd"]),
            ("description", "Encoding for transaction or account data."),
        ])),
        ("TransactionDetails", _OD([
            ("type", "string"),
            ("enum", ["full", "accounts", "signatures", "none"]),
            ("description", "Level of transaction detail to return on block queries."),
        ])),
        ("AccountInfo", _OD([
            ("type", "object"),
            ("description", "On-chain account state."),
            ("nullable", True),
            ("required", ["lamports", "owner", "executable", "rentEpoch", "data"]),
            ("properties", _OD([
                ("lamports", _OD([("type", "integer"), ("format", "int64"), ("description", "Balance in lamports.")])),
                ("owner", _OD([("type", "string"), ("description", "Base-58 program id that owns the account.")])),
                ("executable", _OD([("type", "boolean")])),
                ("rentEpoch", _OD([("type", "integer"), ("format", "int64")])),
                ("space", _OD([("type", "integer"), ("description", "Data length in bytes.")])),
                ("data", _OD([
                    ("description", "Account data; encoding depends on request encoding."),
                    ("oneOf", [
                        _OD([("type", "string")]),
                        _OD([("type", "array"), ("items", _OD([("type", "string")]))]),
                        _OD([("type", "object"), ("additionalProperties", True)]),
                    ]),
                ])),
            ])),
        ])),
        ("UiTokenAmount", _OD([
            ("type", "object"),
            ("required", ["amount", "decimals", "uiAmountString"]),
            ("description", "Token amount with both raw and UI representations."),
            ("properties", _OD([
                ("amount", _OD([("type", "string"), ("description", "Raw amount, ignoring decimals.")])),
                ("decimals", _OD([("type", "integer")])),
                ("uiAmount", _OD([("type", "number"), ("nullable", True)])),
                ("uiAmountString", _OD([("type", "string")])),
            ])),
        ])),
    ])),
    ("responses", _OD([
        ("UnauthorizedError", _OD([
            ("description", "Authentication required or invalid."),
            ("content", _OD([
                ("application/json", _OD([
                    ("schema", _OD([("$ref", "#/components/schemas/JsonRpcErrorResponse")])),
                ])),
            ])),
        ])),
        ("ForbiddenError", _OD([
            ("description", "Insufficient permissions for the request."),
            ("content", _OD([
                ("application/json", _OD([
                    ("schema", _OD([("$ref", "#/components/schemas/JsonRpcErrorResponse")])),
                ])),
            ])),
        ])),
        ("TooManyRequestsError", _OD([
            ("description", "Rate limit exceeded for this tier."),
            ("content", _OD([
                ("application/json", _OD([
                    ("schema", _OD([("$ref", "#/components/schemas/JsonRpcErrorResponse")])),
                ])),
            ])),
        ])),
        ("InternalServerError", _OD([
            ("description", "Unexpected server error."),
            ("content", _OD([
                ("application/json", _OD([
                    ("schema", _OD([("$ref", "#/components/schemas/JsonRpcErrorResponse")])),
                ])),
            ])),
        ])),
    ])),
    ("securitySchemes", _OD([
        ("AuthHeader", _OD([
            ("type", "apiKey"),
            ("in", "header"),
            ("name", "Authorization"),
            ("description", "Pass `Authorization: <api-key>` on each request."),
        ])),
        ("URLParameter", _OD([
            ("type", "apiKey"),
            ("in", "query"),
            ("name", "api_key"),
            ("description", "Pass `?api_key=<api-key>` on the URL."),
        ])),
    ])),
])


# ---------------------------------------------------------------------------
# Helper schema constructors.
# ---------------------------------------------------------------------------

def s_string(desc=None, example=None, **kw):
    o = _OD([("type", "string")])
    if desc:
        o["description"] = desc
    if example is not None:
        o["example"] = example
    o.update(kw)
    return o


def s_int(desc=None, example=None, fmt="int64", **kw):
    o = _OD([("type", "integer"), ("format", fmt)])
    if desc:
        o["description"] = desc
    if example is not None:
        o["example"] = example
    o.update(kw)
    return o


def s_num(desc=None, example=None, **kw):
    o = _OD([("type", "number")])
    if desc:
        o["description"] = desc
    if example is not None:
        o["example"] = example
    o.update(kw)
    return o


def s_bool(desc=None, example=None, **kw):
    o = _OD([("type", "boolean")])
    if desc:
        o["description"] = desc
    if example is not None:
        o["example"] = example
    o.update(kw)
    return o


def s_obj(properties=None, required=None, desc=None, **kw):
    o = _OD([("type", "object")])
    if desc:
        o["description"] = desc
    if required:
        o["required"] = required
    if properties:
        o["properties"] = _OD(properties)
    o.update(kw)
    return o


def s_arr(items, desc=None, **kw):
    o = _OD([("type", "array"), ("items", items)])
    if desc:
        o["description"] = desc
    o.update(kw)
    return o


def s_ref(ref):
    return _OD([("$ref", ref)])


def config_param(extra_props=None, name="config", desc="Optional configuration object. Every field is optional; omit the entire object to use defaults.", required=False):
    """Standard config-object positional parameter.

    All Solana RPC config objects share `commitment` and `minContextSlot`.
    Methods provide additional method-specific keys via `extra_props`. Every
    nested property carries its own description and example so the schema
    renders meaningfully in GitBook.
    """
    props = OrderedDict([
        ("commitment", s_ref("#/components/schemas/Commitment")),
        ("minContextSlot", s_int(
            desc="Minimum slot at which the request can be evaluated. The RPC node will reject the request with a `MinContextSlotNotReached` error if its current root is below this value. Use this for read-after-write consistency in multi-step workflows.",
            example=416990000,
        )),
    ])
    if extra_props:
        for k, v in extra_props.items():
            props[k] = v
    return {
        "name": name,
        "schema_doc": desc,
        "schema": s_obj(properties=props, desc=desc),
        "required": required,
    }


def data_slice_schema():
    """Standard `dataSlice` field used by getAccountInfo, getMultipleAccounts, getProgramAccounts."""
    return s_obj(
        desc="Optional byte range of the account data to return. Use this to fetch only a slice of large accounts and save bandwidth.",
        properties=OrderedDict([
            ("offset", s_int(
                desc="Number of bytes from the start of account data at which the slice begins.",
                example=0,
            )),
            ("length", s_int(
                desc="Number of bytes to include in the slice, starting from `offset`.",
                example=64,
            )),
        ]),
    )


def memcmp_filter_schema():
    """Filter object used by getProgramAccounts."""
    return s_obj(
        desc="A filter that matches accounts whose data length equals `dataSize`, or whose data at `memcmp.offset` equals `memcmp.bytes`. Provide one of the two keys per filter.",
        properties=OrderedDict([
            ("dataSize", s_int(
                desc="Exact account data size, in bytes. Match accounts whose data is exactly this many bytes long.",
                example=165,
            )),
            ("memcmp", s_obj(
                desc="Match accounts whose data at `offset` equals `bytes` (encoded per `encoding`).",
                properties=OrderedDict([
                    ("offset", s_int(desc="Byte offset into the account data.", example=0)),
                    ("bytes", s_string(desc="Bytes to match against, base-58 or base-64.", example="3Mc6vR")),
                    ("encoding", s_string(desc="Encoding for the `bytes` field.", enum=["base58", "base64"], example="base58")),
                ]),
            )),
        ]),
    )


def pubkey_param(name="pubkey", desc="Base-58 encoded public key.", example="83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri"):
    return {
        "name": name,
        "schema_doc": desc,
        "schema": s_string(desc, example=example),
        "required": True,
    }


# ---------------------------------------------------------------------------
# SOLANA RPC method catalog.
# ---------------------------------------------------------------------------

SOLANA_METHODS = []


def add_solana(**method):
    SOLANA_METHODS.append(method)


# Account
add_solana(
    name="getAccountInfo", tag="Account",
    summary="Account info for a single pubkey",
    description="Returns all information associated with the account of provided Pubkey",
    params=[
        pubkey_param(),
        config_param(extra_props={
            "encoding": s_ref("#/components/schemas/Encoding"),
            "dataSlice": data_slice_schema(),
        }),
    ],
    params_example=["83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri", {"encoding": "base64", "commitment": "finalized"}],
    result_schema=s_obj(required=["context", "value"], properties=[
        ("context", s_ref("#/components/schemas/Context")),
        ("value", s_ref("#/components/schemas/AccountInfo")),
    ]),
    result_example={"context": {"slot": 416997240, "apiVersion": "3.1.10"}, "value": {"lamports": 1000000, "owner": "11111111111111111111111111111111", "executable": False, "rentEpoch": 18446744073709551615, "space": 0, "data": ["", "base64"]}},
)

add_solana(
    name="getBalance", tag="Account",
    summary="Lamport balance for a pubkey",
    description="Returns the lamport balance of the account of provided Pubkey. The balance is returned in lamports, where 1 SOL = 1,000,000,000 lamports.",
    params=[pubkey_param(), config_param()],
    params_example=["83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri", {"commitment": "finalized"}],
    result_schema=s_obj(required=["context", "value"], properties=[
        ("context", s_ref("#/components/schemas/Context")),
        ("value", s_int(desc="Balance in lamports.", example=1000000)),
    ]),
    result_example={"context": {"slot": 416997240, "apiVersion": "3.1.10"}, "value": 1000000},
)

add_solana(
    name="getMultipleAccounts", tag="Account",
    summary="Account info for many pubkeys",
    description="Returns account information for multiple accounts in a single request. This is more efficient than making multiple getAccountInfo calls when you need to fetch data from several accounts at once. You can request up to 100 accounts per call.",
    params=[
        {"name": "pubkeys", "schema_doc": "Array of base-58 encoded pubkeys, max 100.",
         "schema": s_arr(s_string(desc="Account pubkey, base-58.", example="83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri"), desc="Pubkeys to query, max 100 per request. Order is preserved in the response.", maxItems=100, minItems=1), "required": True},
        config_param(extra_props={
            "encoding": s_ref("#/components/schemas/Encoding"),
            "dataSlice": data_slice_schema(),
        }),
    ],
    params_example=[["83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri", "11111111111111111111111111111111"], {"encoding": "base64"}],
    result_schema=s_obj(required=["context", "value"], properties=[
        ("context", s_ref("#/components/schemas/Context")),
        ("value", s_arr(s_ref("#/components/schemas/AccountInfo"), desc="One account per requested pubkey, in order. Null for pubkeys that don't exist.")),
    ]),
    result_example={"context": {"slot": 416997240, "apiVersion": "3.1.10"}, "value": [{"lamports": 1000000, "owner": "11111111111111111111111111111111", "executable": False, "rentEpoch": 0, "space": 0, "data": ["", "base64"]}, None]},
)

add_solana(
    name="getProgramAccounts", tag="Account",
    summary="All accounts owned by a program",
    description="Returns all accounts owned by a given program. This method is useful for finding all accounts associated with a specific program, such as all token accounts for a particular token mint or all accounts created by a custom program. You can apply filters to narrow down the results. SPL/SPL2022 Token Program Requirements: When querying SPL or SPL2022 token programs, the configuration object must include: filters (array, required): An array of filters to apply to the accounts. Must contain the dataSize filter. Must be one of the known lengths for SPL/SPL2022 program accounts (mint= 82 , token= 165 ) or a larger value when filtering for SPL2022 accounts with extensions. When filtering for multisig accounts, the size must be 355 for accounts of both programs. When filtering for token accounts : Must contain at least one memcmp filter. Only the mint ( offset = 0 , 32 bytes data length) and the owner ( offset = 32 , 32 bytes data length) filters are supported.",
    params=[
        pubkey_param(name="programId", desc="Program pubkey, base-58."),
        config_param(extra_props={
            "encoding": s_ref("#/components/schemas/Encoding"),
            "dataSlice": s_obj(properties={"offset": s_int(), "length": s_int()}),
            "filters": s_arr(memcmp_filter_schema(), desc="Optional list of filters. Each filter narrows the result set; the server intersects them. Use `dataSize` to filter by account data length, and `memcmp` to filter by byte-equal at a given offset."),
            "withContext": s_bool(desc="If true, wrap the response in a `{context, value}` envelope. Default is false (return the array directly).", example=True),
        }),
    ],
    params_example=["TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq", {"encoding": "base64", "filters": [{"dataSize": 165}]}],
    result_schema=s_arr(s_obj(required=["pubkey", "account"], properties=[
        ("pubkey", s_string()), ("account", s_ref("#/components/schemas/AccountInfo")),
    ]), desc="Array of {pubkey, account} pairs."),
    result_example=[{"pubkey": "83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri", "account": {"lamports": 2039280, "owner": "TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq", "executable": False, "rentEpoch": 0, "space": 165, "data": ["", "base64"]}}],
)

add_solana(
    name="getTokenAccountBalance", tag="Account",
    summary="Token account balance",
    description="Returns the token balance of an SPL Token account.",
    params=[pubkey_param(desc="Token account pubkey, base-58.", example="7UVpfyV3PzWxNw3pcU88WGGgC4XSiTNVTPMK6P7vrqCi"), config_param()],
    params_example=["7UVpfyV3PzWxNw3pcU88WGGgC4XSiTNVTPMK6P7vrqCi", {"commitment": "finalized"}],
    result_schema=s_obj(required=["context", "value"], properties=[
        ("context", s_ref("#/components/schemas/Context")),
        ("value", s_ref("#/components/schemas/UiTokenAmount")),
    ]),
    result_example={"context": {"slot": 416997240, "apiVersion": "3.1.10"}, "value": {"amount": "1000000", "decimals": 6, "uiAmount": 1.0, "uiAmountString": "1"}},
)

add_solana(
    name="getTokenAccountsByDelegate", tag="Account",
    summary="Token accounts by delegate",
    description="Returns all SPL Token accounts by approved delegate. This method is essential for finding token accounts where a specific address has been granted delegation permissions to spend tokens on behalf of the owner.",
    params=[
        pubkey_param(name="delegate", desc="Delegate pubkey, base-58."),
        {"name": "filter", "schema_doc": "Filter by mint or program id (one of).",
         "schema": s_obj(desc="Filter the result set. Provide exactly one of `mint` or `programId`.", properties=OrderedDict([("mint", s_string(desc="Filter to a specific token mint address (base-58).", example="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")), ("programId", s_string(desc="Filter to a token program (base-58). Typically the SPL Token or Token-2022 program id.", example="TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq"))])),
         "required": True},
        config_param(extra_props={"encoding": s_ref("#/components/schemas/Encoding")}),
    ],
    params_example=["83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri", {"programId": "TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq"}, {"encoding": "jsonParsed"}],
    result_schema=s_obj(required=["context", "value"], properties=[
        ("context", s_ref("#/components/schemas/Context")),
        ("value", s_arr(s_obj(properties={"pubkey": s_string(), "account": s_ref("#/components/schemas/AccountInfo")}))),
    ]),
    result_example={"context": {"slot": 416997240, "apiVersion": "3.1.10"}, "value": []},
)

add_solana(
    name="getTokenAccountsByOwner", tag="Account",
    summary="Token accounts by owner",
    description="Returns all SPL Token accounts by token owner.",
    params=[
        pubkey_param(name="owner", desc="Owner pubkey, base-58."),
        {"name": "filter", "schema_doc": "Filter by mint or program id (one of).",
         "schema": s_obj(desc="Filter the result set. Provide exactly one of `mint` or `programId`.", properties=OrderedDict([("mint", s_string(desc="Filter to a specific token mint address (base-58).", example="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")), ("programId", s_string(desc="Filter to a token program (base-58). Typically the SPL Token or Token-2022 program id.", example="TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq"))])), "required": True},
        config_param(extra_props={"encoding": s_ref("#/components/schemas/Encoding")}),
    ],
    params_example=["83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri", {"programId": "TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq"}, {"encoding": "jsonParsed"}],
    result_schema=s_obj(required=["context", "value"], properties=[
        ("context", s_ref("#/components/schemas/Context")),
        ("value", s_arr(s_obj(properties={"pubkey": s_string(), "account": s_ref("#/components/schemas/AccountInfo")}))),
    ]),
    result_example={"context": {"slot": 416997240, "apiVersion": "3.1.10"}, "value": []},
)

add_solana(
    name="getTokenLargestAccounts", tag="Account",
    summary="20 largest accounts of a token",
    description="Returns the 20 largest accounts of a particular SPL Token type. This method is essential for analyzing token distribution, identifying whale accounts, and understanding token concentration patterns.",
    params=[pubkey_param(name="mint", desc="Token mint pubkey, base-58."), config_param()],
    params_example=["EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"],
    result_schema=s_obj(required=["context", "value"], properties=[
        ("context", s_ref("#/components/schemas/Context")),
        ("value", s_arr(s_obj(properties={
            "address": s_string(), "amount": s_string(), "decimals": s_int(),
            "uiAmount": s_num(nullable=True), "uiAmountString": s_string(),
        }))),
    ]),
    result_example={"context": {"slot": 416997240, "apiVersion": "3.1.10"}, "value": [{"address": "7UVpfyV3PzWxNw3pcU88WGGgC4XSiTNVTPMK6P7vrqCi", "amount": "1000000", "decimals": 6, "uiAmount": 1.0, "uiAmountString": "1"}]},
)

add_solana(
    name="getTokenSupply", tag="Account",
    summary="Total supply of a token",
    description="Returns the total supply of an SPL Token type. This method is essential for understanding token economics, monitoring token distribution, and tracking token supply changes over time.",
    params=[pubkey_param(name="mint", desc="Token mint pubkey, base-58."), config_param()],
    params_example=["EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"],
    result_schema=s_obj(required=["context", "value"], properties=[
        ("context", s_ref("#/components/schemas/Context")),
        ("value", s_ref("#/components/schemas/UiTokenAmount")),
    ]),
    result_example={"context": {"slot": 416997240, "apiVersion": "3.1.10"}, "value": {"amount": "9046067177782798", "decimals": 6, "uiAmount": 9046067177.782799, "uiAmountString": "9046067177.782798"}},
)

# Block
add_solana(
    name="getBlock", tag="Block",
    summary="Block by slot",
    description="Returns identity and transaction information about a confirmed block in the ledger. Provides detailed block data including all transactions and their metadata.",
    params=[
        {"name": "slot", "schema_doc": "Slot number to fetch.", "schema": s_int(desc="Slot number.", example=416997240), "required": True},
        config_param(extra_props={
            "encoding": s_ref("#/components/schemas/Encoding"),
            "transactionDetails": s_ref("#/components/schemas/TransactionDetails"),
            "rewards": s_bool(desc="Include block rewards in the response. Default false.", example=False),
            "maxSupportedTransactionVersion": s_int(desc="0 includes versioned transactions; omit for legacy-only."),
        }),
    ],
    params_example=[416997240, {"maxSupportedTransactionVersion": 0, "transactionDetails": "full"}],
    result_schema=s_obj(required=["blockhash", "previousBlockhash", "parentSlot", "transactions", "blockHeight"], properties=[
        ("blockhash", s_string()), ("previousBlockhash", s_string()),
        ("parentSlot", s_int()), ("blockHeight", s_int()),
        ("blockTime", s_int(nullable=True)),
        ("transactions", s_arr(s_obj(additionalProperties=True))),
        ("rewards", s_arr(s_obj(additionalProperties=True))),
    ]),
    result_example={"blockhash": "3Eq21vXNB5s86c62bVuUfTeaMif1N2kUqRPBmGRJhyTA", "previousBlockhash": "mfcyqEXB3DnHXki6KjjmZck6YjmZLvpAByy2fj4nh6B", "parentSlot": 416997239, "blockHeight": 395090168, "blockTime": 1777683570, "transactions": [], "rewards": []},
)

add_solana(
    name="getBlockHeight", tag="Block",
    summary="Current block height",
    description="Returns the current block height of the node. Block height is the number of blocks that have been produced since the genesis block. This is different from slot numbers, as blocks represent confirmed batches of transactions.",
    params=[config_param()],
    params_example=[{"commitment": "finalized"}],
    result_schema=s_int(desc="Current block height.", example=395090168),
    result_example=395090168,
)

add_solana(
    name="getBlocks", tag="Block",
    summary="Confirmed blocks in a range",
    description="Returns a list of confirmed blocks between two slots",
    params=[
        {"name": "startSlot", "schema_doc": "Start slot (inclusive).", "schema": s_int(example=416997230), "required": True},
        {"name": "endSlot", "schema_doc": "End slot (inclusive).", "schema": s_int(example=416997240), "required": False},
        config_param(),
    ],
    params_example=[416997230, 416997240],
    result_schema=s_arr(s_int(), desc="Confirmed slots."),
    result_example=[416997230, 416997231, 416997234, 416997235, 416997240],
)

add_solana(
    name="getBlocksWithLimit", tag="Block",
    summary="Confirmed blocks starting at slot",
    description="Returns a list of confirmed blocks starting at the given slot. This method provides an efficient way to retrieve a range of sequential block slots, which is useful for block explorers, analytics tools, and applications that need to process historical blockchain data in batches. Important : The limit must be no more than 500,000 blocks higher than the start_slot.",
    params=[
        {"name": "startSlot", "schema_doc": "Start slot.", "schema": s_int(example=416997230), "required": True},
        {"name": "limit", "schema_doc": "Maximum number of blocks (max 500,000).", "schema": s_int(example=10, maximum=500000), "required": True},
        config_param(),
    ],
    params_example=[416997230, 10],
    result_schema=s_arr(s_int()),
    result_example=[416997230, 416997231, 416997234, 416997235, 416997240, 416997242, 416997243, 416997244, 416997245, 416997246],
)

add_solana(
    name="getBlockTime", tag="Block",
    summary="Estimated production time of a block",
    description="Returns the estimated production time of a block. Each validator reports their UTC time to the ledger on a regular interval by intermittently adding a timestamp to a Vote for a particular block. A requested block's time is calculated from the stake-weighted mean of the Vote timestamps in a set of recent blocks recorded on the ledger.",
    params=[{"name": "slot", "schema_doc": "Slot number.", "schema": s_int(example=416997240), "required": True}],
    params_example=[378967388],
    result_schema=s_int(nullable=True, desc="Unix timestamp seconds, or null if unavailable."),
    result_example=1777683570,
)

add_solana(
    name="getBlockCommitment", tag="Block",
    summary="Commitment for a block",
    description="Returns commitment for particular block. This method provides information about the cluster stake that has voted on a specific block at each depth.",
    params=[{"name": "slot", "schema_doc": "Slot number.", "schema": s_int(example=416997240), "required": True}],
    params_example=[378967388],
    result_schema=s_obj(properties=[
        ("commitment", s_arr(s_int(), nullable=True)),
        ("totalStake", s_int()),
    ]),
    result_example={"commitment": [0]*31 + [999999999999], "totalStake": 999999999999},
)

add_solana(
    name="getBlockProduction", tag="Block",
    summary="Recent block production",
    description="Returns recent block production information from the current or previous epoch",
    params=[config_param(extra_props={
        "identity": s_string(desc="Filter to a single validator identity (base-58 pubkey). Omit to include all validators.", example="FbXMxhgoCYbZ4dWaCVzJWeFqW2tQ8sR82Hi8YyQrEaxR"),
        "range": s_obj(desc="Slot range to summarize block production over. Defaults to the current epoch when omitted.", properties=OrderedDict([("firstSlot", s_int(desc="First slot in the range, inclusive.", example=416997000)), ("lastSlot", s_int(desc="Last slot in the range, inclusive.", example=416997240))])),
    })],
    params_example=[{"commitment": "finalized"}],
    result_schema=s_obj(required=["context", "value"], properties=[
        ("context", s_ref("#/components/schemas/Context")),
        ("value", s_obj(properties={
            "byIdentity": s_obj(additionalProperties=s_arr(s_int()), desc="Identity → [leaderSlots, blocksProduced]."),
            "range": s_obj(properties={"firstSlot": s_int(), "lastSlot": s_int()}),
        })),
    ]),
    result_example={"context": {"slot": 416997240, "apiVersion": "3.1.10"}, "value": {"byIdentity": {"FbXMxhgoCYbZ4dWaCVzJWeFqW2tQ8sR82Hi8YyQrEaxR": [144, 144]}, "range": {"firstSlot": 349200000, "lastSlot": 349392648}}},
)

# Cluster
add_solana(
    name="getClusterNodes", tag="Cluster",
    summary="All cluster nodes",
    description="Returns information about all the nodes participating in the cluster. This includes details about each node's network addresses, version, and configuration parameters.",
    params=[],
    params_example=[],
    result_schema=s_arr(s_obj(properties={
        "pubkey": s_string(), "gossip": s_string(nullable=True), "tpu": s_string(nullable=True),
        "rpc": s_string(nullable=True), "version": s_string(nullable=True),
        "featureSet": s_int(nullable=True), "shredVersion": s_int(nullable=True),
    })),
    result_example=[{"pubkey": "FbXMxhgoCYbZ4dWaCVzJWeFqW2tQ8sR82Hi8YyQrEaxR", "gossip": "203.0.113.10:8001", "tpu": "203.0.113.10:8003", "rpc": None, "version": "3.1.10", "featureSet": 1620780344, "shredVersion": 0}],
)

add_solana(
    name="getEpochInfo", tag="Cluster",
    summary="Current epoch info",
    description="Returns information about the current epoch including the current slot, block height, epoch number, slot index within the epoch, total slots in the epoch, and transaction count.",
    params=[config_param()],
    params_example=[{"commitment": "finalized"}],
    result_schema=s_obj(properties=[
        ("absoluteSlot", s_int()), ("blockHeight", s_int()), ("epoch", s_int()),
        ("slotIndex", s_int()), ("slotsInEpoch", s_int()),
        ("transactionCount", s_int(nullable=True)),
    ]),
    result_example={"absoluteSlot": 416997240, "blockHeight": 395090168, "epoch": 965, "slotIndex": 117240, "slotsInEpoch": 432000, "transactionCount": 509155823874},
)

add_solana(
    name="getEpochSchedule", tag="Cluster",
    summary="Epoch schedule",
    description="Returns the genesis epoch schedule that this cluster is using.",
    params=[],
    params_example=[],
    result_schema=s_obj(properties=[
        ("slotsPerEpoch", s_int()), ("leaderScheduleSlotOffset", s_int()),
        ("warmup", s_bool()), ("firstNormalEpoch", s_int()), ("firstNormalSlot", s_int()),
    ]),
    result_example={"slotsPerEpoch": 432000, "leaderScheduleSlotOffset": 432000, "warmup": False, "firstNormalEpoch": 0, "firstNormalSlot": 0},
)

add_solana(
    name="getGenesisHash", tag="Cluster",
    summary="Genesis hash",
    description="Returns the genesis hash of the Solana network. The genesis hash is a unique identifier for the blockchain network that represents the initial state of the ledger.",
    params=[],
    params_example=[],
    result_schema=s_string(desc="Base-58 genesis hash."),
    result_example="5eykt4UsFv8P8NJdTREpY1vzqKqZKvdpKuc147dw2N9d",
)

add_solana(
    name="getHealth", tag="Cluster",
    summary="Node health",
    description="Returns the current health of the node. A healthy node is one that is within 25 slots of the latest cluster confirmed slot. This method is useful for monitoring node synchronization status and determining if the node is keeping up with the network.",
    params=[],
    params_example=[],
    result_schema=s_string(enum=["ok"], desc="Node health status."),
    result_example="ok",
)

add_solana(
    name="getIdentity", tag="Cluster",
    summary="Node identity",
    description="Returns the identity pubkey for the current node. The identity pubkey uniquely identifies the validator node in the Solana network.",
    params=[],
    params_example=[],
    result_schema=s_obj(properties=[("identity", s_string())]),
    result_example={"identity": "9bupGu2BbLbPCb1ZUAswM3GBVfnKsYWBJjJixD5N5cYm"},
)

add_solana(
    name="getVersion", tag="Cluster",
    summary="Solana version",
    description="Returns the current Solana version information running on the node.",
    params=[],
    params_example=[],
    result_schema=s_obj(properties=[
        ("solana-core", s_string()), ("feature-set", s_int(fmt="int32")),
    ]),
    result_example={"solana-core": "3.1.10", "feature-set": 1620780344},
)

# Fees
add_solana(
    name="getFeeForMessage", tag="Fees",
    summary="Estimate fee for a message",
    description="Get the fee the network will charge for a particular Message. Version Restriction : This method is only available in solana-core v1.9 or newer. Please use getFees for solana-core v1.8 and below.",
    params=[
        {"name": "message", "schema_doc": "Base-64 encoded compiled transaction message (the `Message`, not a full transaction). Used by `getFeeForMessage`.", "schema": s_string(desc="Base-64 encoded compiled message.", example="AQABA0PJ8nGUKkR2lKZ8VcWQYWQzTGYYNCPdjhq2WaqLNUowVnPB6Q=="), "required": True},
        config_param(),
    ],
    params_example=["AQABA0PJ8nGUKkR2lKZ8VcWQYWQzTGYYNCPdjhq2WaqLNUowVnPB6Q==", {"commitment": "processed"}],
    result_schema=s_obj(required=["context", "value"], properties=[
        ("context", s_ref("#/components/schemas/Context")),
        ("value", s_int(nullable=True, desc="Fee in lamports, or null if message could not be decoded.")),
    ]),
    result_example={"context": {"slot": 416997240, "apiVersion": "3.1.10"}, "value": 5000},
)

add_solana(
    name="getLatestBlockhash", tag="Fees",
    summary="Latest blockhash",
    description="Returns the latest blockhash. This is essential for creating transactions as the blockhash is required for transaction validity.",
    params=[config_param()],
    params_example=[{"commitment": "finalized"}],
    result_schema=s_obj(required=["context", "value"], properties=[
        ("context", s_ref("#/components/schemas/Context")),
        ("value", s_obj(properties=[("blockhash", s_string()), ("lastValidBlockHeight", s_int())])),
    ]),
    result_example={"context": {"slot": 416997240, "apiVersion": "3.1.10"}, "value": {"blockhash": "3Eq21vXNB5s86c62bVuUfTeaMif1N2kUqRPBmGRJhyTA", "lastValidBlockHeight": 367212294}},
)

add_solana(
    name="isBlockhashValid", tag="Fees",
    summary="Check blockhash validity",
    description="Returns whether a blockhash is still valid or not.",
    params=[
        {"name": "blockhash", "schema_doc": "Base-58 blockhash.", "schema": s_string(example="3Eq21vXNB5s86c62bVuUfTeaMif1N2kUqRPBmGRJhyTA"), "required": True},
        config_param(),
    ],
    params_example=["3Eq21vXNB5s86c62bVuUfTeaMif1N2kUqRPBmGRJhyTA", {"commitment": "processed"}],
    result_schema=s_obj(required=["context", "value"], properties=[
        ("context", s_ref("#/components/schemas/Context")),
        ("value", s_bool(desc="True if blockhash is still valid.")),
    ]),
    result_example={"context": {"slot": 416997240, "apiVersion": "3.1.10"}, "value": True},
)

add_solana(
    name="getMinimumBalanceForRentExemption", tag="Fees",
    summary="Min balance for rent exemption",
    description="Returns the minimum balance required to make an account rent exempt on the Solana blockchain. Rent is a mechanism on Solana that ensures efficient usage of blockchain resources by requiring accounts to maintain a minimum balance proportional to the amount of data they store. Accounts that maintain this minimum balance are \"rent exempt\" and will never have their balance reduced by the network.",
    params=[
        {"name": "dataLength", "schema_doc": "Account data length in bytes.", "schema": s_int(example=165), "required": True},
        config_param(),
    ],
    params_example=[165, {"commitment": "finalized"}],
    result_schema=s_int(desc="Minimum balance in lamports.", example=2039280),
    result_example=2039280,
)

add_solana(
    name="getRecentPrioritizationFees", tag="Fees",
    summary="Recent prioritization fees",
    description="Returns a list of prioritization fees from recent blocks to help estimate appropriate priority fees for transactions. The method returns data from up to 150 recent blocks stored in the node's prioritization-fee cache. When account addresses are provided, the response reflects the fees needed to land a transaction that locks all specified accounts as writable, helping estimate fees for transactions with account contention. This data is essential for applications that need to dynamically adjust priority fees based on current network conditions, ensuring transactions are processed quickly without overpaying. The fees are expressed in microlamports per compute unit, where 1 microlamport = 0.000001 lamports.",
    params=[{"name": "addresses", "schema_doc": "Optional list of account pubkeys (max 128). Returned fees are scoped to recent blocks that referenced any of these accounts.",
             "schema": s_arr(s_string(desc="Account pubkey, base-58.", example="83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri"), desc="Account pubkeys (max 128). Omit or pass an empty array for cluster-wide stats."), "required": False}],
    params_example=[["83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri"]],
    result_schema=s_arr(s_obj(properties=[("slot", s_int()), ("prioritizationFee", s_int())])),
    result_example=[{"slot": 416997125, "prioritizationFee": 0}, {"slot": 416997126, "prioritizationFee": 0}, {"slot": 416997127, "prioritizationFee": 1000}],
)

# Transactions
add_solana(
    name="getSignaturesForAddress", tag="Transactions",
    summary="Signatures involving an address",
    description="Returns signatures for confirmed transactions that include the given address in their accountKeys list. Returns signatures backwards in time from the provided signature or most recent confirmed block. This method is essential for transaction history, wallet activity feeds, and building transaction explorers.",
    params=[
        pubkey_param(),
        config_param(extra_props={
            "limit": s_int(desc="Maximum number of signatures to return. Range 1–1000; default 1000.", example=10, minimum=1, maximum=1000),
            "before": s_string(desc="Start the search before this signature (exclusive). Use to paginate backwards in history.", example="4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa"),
            "until": s_string(desc="Search until this signature (inclusive). Use to bound the search to a recent window.", example="4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa"),
        }),
    ],
    params_example=["83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri", {"limit": 10}],
    result_schema=s_arr(s_obj(properties=[
        ("signature", s_string()), ("slot", s_int()),
        ("err", s_obj(nullable=True, additionalProperties=True)),
        ("memo", s_string(nullable=True)), ("blockTime", s_int(nullable=True)),
        ("confirmationStatus", s_string(enum=["processed", "confirmed", "finalized"])),
    ])),
    result_example=[{"signature": "4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa", "slot": 349392648, "err": None, "memo": None, "blockTime": 1777683570, "confirmationStatus": "finalized"}],
)

add_solana(
    name="getSignatureStatuses", tag="Transactions",
    summary="Signature confirmation statuses",
    description="Returns the statuses of a list of transaction signatures. This method is essential for checking whether transactions have been confirmed, failed, or are still processing. It's commonly used by wallets and dApps to monitor transaction status and provide real-time feedback to users. You can check up to 256 signatures in a single request.",
    params=[
        {"name": "signatures", "schema_doc": "Array of base-58 transaction signatures (max 256).", "schema": s_arr(s_string(desc="Transaction signature, base-58.", example="4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa"), desc="Signatures to look up. Result array preserves order; missing signatures appear as null."), "required": True},
        config_param(extra_props={"searchTransactionHistory": s_bool(desc="If true, look up signatures in the long-term ledger archive in addition to recent slots. Slower but covers older transactions. Default false.", example=True)}),
    ],
    params_example=[["4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa"], {"searchTransactionHistory": True}],
    result_schema=s_obj(required=["context", "value"], properties=[
        ("context", s_ref("#/components/schemas/Context")),
        ("value", s_arr(s_obj(nullable=True, properties={
            "slot": s_int(), "confirmations": s_int(nullable=True),
            "err": s_obj(nullable=True, additionalProperties=True),
            "confirmationStatus": s_string(enum=["processed", "confirmed", "finalized"]),
        }, desc="Status object, or null if signature is unknown."))),
    ]),
    result_example={"context": {"slot": 416997240, "apiVersion": "3.1.10"}, "value": [{"slot": 349392640, "confirmations": None, "err": None, "confirmationStatus": "finalized"}]},
)

add_solana(
    name="getTransaction", tag="Transactions",
    summary="Transaction by signature",
    description="Returns transaction details for a confirmed transaction signature. Provides comprehensive information about the transaction including its status, fees, logs, and account changes. This method is essential for transaction explorers, wallets, and dApps that need to analyze transaction execution details. Important : For most modern Solana transactions, you must include maxSupportedTransactionVersion: 0 in the request parameters, otherwise the request will fail with an error if the transaction is a versioned transaction.",
    params=[
        {"name": "signature", "schema_doc": "Base-58 transaction signature.", "schema": s_string(desc="Transaction signature, base-58.", example="4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa"), "required": True},
        config_param(extra_props=OrderedDict([
            ("encoding", s_ref("#/components/schemas/Encoding")),
            ("maxSupportedTransactionVersion", s_int(desc="Highest transaction version the client can handle. Set to 0 to receive versioned (v0) transactions; omit to receive only legacy (pre-v0) transactions.", example=0)),
        ])),
    ],
    params_example=["4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa", {"maxSupportedTransactionVersion": 0}],
    result_schema=s_obj(nullable=True, properties=[
        ("slot", s_int()), ("blockTime", s_int(nullable=True)),
        ("transaction", s_obj(additionalProperties=True)),
        ("meta", s_obj(additionalProperties=True, nullable=True)),
        ("version", _OD([("oneOf", [s_int(), s_string()])])),
    ]),
    result_example={"slot": 349392648, "blockTime": 1777683570, "transaction": {"signatures": ["..."], "message": {}}, "meta": {"err": None, "fee": 5000, "preBalances": [1000000], "postBalances": [995000]}, "version": 0},
)

add_solana(
    name="getTransactionCount", tag="Transactions",
    summary="Total transaction count",
    description="Returns the current transaction count from the ledger. This method provides a cumulative count of all transactions that have been processed by the Solana network since genesis.",
    params=[config_param()],
    params_example=[{"commitment": "finalized"}],
    result_schema=s_int(),
    result_example=509155823874,
)

add_solana(
    name="sendTransaction", tag="Transactions",
    summary="Submit a signed transaction",
    description="Submits a signed transaction to the cluster for processing and returns the transaction signature if successful. This is the primary method for executing transactions on the Solana network. The transaction must be fully signed and serialized before submission. The method provides various options for controlling transaction processing behavior, including preflight checks, retry logic, and encoding formats. Transactions that fail preflight checks or network validation will return detailed error information.",
    params=[
        {"name": "transaction", "schema_doc": "Fully-signed transaction encoded per the chosen `encoding` (base-58 by default, base-64 recommended).", "schema": s_string(desc="Fully-signed encoded transaction.", example="4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa"), "required": True},
        config_param(extra_props={
            "skipPreflight": s_bool(desc="If true, skip the preflight transaction simulation that verifies signature, blockhash, and account state before submission. Default false.", example=False, default=False),
            "preflightCommitment": s_ref("#/components/schemas/Commitment"),
            "encoding": s_ref("#/components/schemas/Encoding"),
            "maxRetries": s_int(desc="Maximum number of retries when forwarding to the leader. Default unlimited (until blockhash expires).", example=0),
        }),
    ],
    params_example=["4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa", {"skipPreflight": False, "preflightCommitment": "processed"}],
    result_schema=s_string(desc="Transaction signature, base-58."),
    result_example="4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa",
)

add_solana(
    name="simulateTransaction", tag="Transactions",
    summary="Simulate a transaction",
    description="Simulates sending a transaction to get the effects that would occur if the transaction was committed. The simulation runs against the current state of the blockchain and provides detailed information including logs, account changes, compute units consumed, and any errors that would occur during execution.",
    params=[
        {"name": "transaction", "schema_doc": "Encoded transaction (signed or unsigned, depending on `sigVerify`).", "schema": s_string(desc="Encoded transaction string.", example="4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa"), "required": True},
        config_param(extra_props={
            "sigVerify": s_bool(desc="If true, verify the transaction signatures during simulation. Cannot be combined with `replaceRecentBlockhash`. Default false.", example=False, default=False),
            "replaceRecentBlockhash": s_bool(desc="If true, replace the transaction's recent blockhash with the latest known blockhash before simulating. Cannot be combined with `sigVerify`. Default false.", example=True, default=False),
            "encoding": s_ref("#/components/schemas/Encoding"),
            "accounts": s_obj(desc="Specifies which accounts to return after simulation. Use to inspect account state changes the transaction would produce.", properties=OrderedDict([("addresses", s_arr(s_string(desc="Account pubkey, base-58.", example="83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri"), desc="Pubkeys of accounts whose post-simulation state to return.")), ("encoding", s_ref("#/components/schemas/Encoding"))])),
        }),
    ],
    params_example=["4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa", {"sigVerify": False, "replaceRecentBlockhash": True}],
    result_schema=s_obj(required=["context", "value"], properties=[
        ("context", s_ref("#/components/schemas/Context")),
        ("value", s_obj(properties={
            "err": s_obj(nullable=True, additionalProperties=True),
            "logs": s_arr(s_string()),
            "accounts": s_arr(s_ref("#/components/schemas/AccountInfo"), nullable=True),
            "unitsConsumed": s_int(),
            "returnData": s_obj(nullable=True, properties={"programId": s_string(), "data": s_arr(s_string())}),
        })),
    ]),
    result_example={"context": {"slot": 416997240, "apiVersion": "3.1.10"}, "value": {"err": None, "logs": ["Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success"], "accounts": None, "unitsConsumed": 200, "returnData": None}},
)

# Slots
add_solana(
    name="getSlot", tag="Slots",
    summary="Current slot",
    description="Returns the slot that has reached the given or default commitment level.",
    params=[config_param()],
    params_example=[{"commitment": "finalized"}],
    result_schema=s_int(example=416997240),
    result_example=416997240,
)

add_solana(
    name="getSlotLeader", tag="Slots",
    summary="Current slot leader",
    description="Returns the current slot leader.",
    params=[config_param()],
    params_example=[{"commitment": "finalized"}],
    result_schema=s_string(),
    result_example="DRpbCBMxVnDK7maPM5tGv6MvB3v1sRMC86PZ8okm21hy",
)

add_solana(
    name="getSlotLeaders", tag="Slots",
    summary="Slot leaders for a range",
    description="Returns the slot leaders for a given slot range. This method provides the sequence of validators scheduled to produce blocks for consecutive slots, which is essential for understanding the upcoming block production schedule on the Solana network.",
    params=[
        {"name": "startSlot", "schema_doc": "First slot.", "schema": s_int(example=416997230), "required": True},
        {"name": "limit", "schema_doc": "Number of leaders to return (1–5000).", "schema": s_int(example=10), "required": True},
    ],
    params_example=[416997230, 10],
    result_schema=s_arr(s_string()),
    result_example=["FbXMxhgoCYbZ4dWaCVzJWeFqW2tQ8sR82Hi8YyQrEaxR"] * 10,
)

add_solana(
    name="getLeaderSchedule", tag="Slots",
    summary="Leader schedule for an epoch",
    description="Returns the leader schedule for an epoch, showing which validator is assigned to each slot.",
    params=[
        {"name": "slot", "schema_doc": "Slot to compute the epoch from (optional).", "schema": s_int(nullable=True), "required": False},
        config_param(extra_props={"identity": s_string(desc="Filter to a single validator identity (base-58 pubkey).", example="FbXMxhgoCYbZ4dWaCVzJWeFqW2tQ8sR82Hi8YyQrEaxR")}),
    ],
    params_example=[None, {"commitment": "finalized"}],
    result_schema=_OD([
        ("type", "object"), ("nullable", True),
        ("additionalProperties", s_arr(s_int())),
        ("description", "Map of leader pubkey to ordered list of slot indices."),
    ]),
    result_example={"FbXMxhgoCYbZ4dWaCVzJWeFqW2tQ8sR82Hi8YyQrEaxR": [0, 4, 8, 12, 16]},
)

# Stake / Validators / Inflation
add_solana(
    name="getStakeMinimumDelegation", tag="Stake",
    summary="Minimum stake delegation",
    description="Returns the minimum delegation amount required for staking SOL on the Solana network, expressed in lamports.",
    params=[config_param()],
    params_example=[{"commitment": "finalized"}],
    result_schema=s_obj(required=["context", "value"], properties=[
        ("context", s_ref("#/components/schemas/Context")),
        ("value", s_int(desc="Minimum delegation in lamports.")),
    ]),
    result_example={"context": {"slot": 416997240, "apiVersion": "3.1.10"}, "value": 1},
)

add_solana(
    name="getVoteAccounts", tag="Validators",
    summary="Vote accounts",
    description="Returns the account info and associated stake for all the voting accounts in the current bank.",
    params=[config_param(extra_props=OrderedDict([
        ("votePubkey", s_string(desc="Filter to a single validator vote account, base-58.", example="FbXMxhgoCYbZ4dWaCVzJWeFqW2tQ8sR82Hi8YyQrEaxR")),
        ("keepUnstakedDelinquents", s_bool(desc="If true, include delinquent validators with zero active stake.", example=False)),
        ("delinquentSlotDistance", s_int(desc="Number of slots behind the cluster a validator must be to be considered delinquent. Default 128.", example=128)),
    ]))],
    params_example=[{"commitment": "finalized"}],
    result_schema=s_obj(properties=[
        ("current", s_arr(s_obj(additionalProperties=True))),
        ("delinquent", s_arr(s_obj(additionalProperties=True))),
    ]),
    result_example={"current": [{"votePubkey": "FbXMxhgoCYbZ4dWaCVzJWeFqW2tQ8sR82Hi8YyQrEaxR", "nodePubkey": "FbXMxhgoCYbZ4dWaCVzJWeFqW2tQ8sR82Hi8YyQrEaxR", "activatedStake": 99999999999, "epochVoteAccount": True, "commission": 5, "lastVote": 349392648, "rootSlot": 349392600}], "delinquent": []},
)

add_solana(
    name="getInflationGovernor", tag="Inflation",
    summary="Inflation governor",
    description="Returns the current inflation governor, which contains the parameters that control Solana's inflation schedule including initial rates, taper rates, terminal rates, and foundation allocation.",
    params=[config_param()],
    params_example=[{"commitment": "finalized"}],
    result_schema=s_obj(properties=[
        ("initial", s_num()), ("terminal", s_num()), ("taper", s_num()),
        ("foundation", s_num()), ("foundationTerm", s_num()),
    ]),
    result_example={"initial": 0.08, "terminal": 0.015, "taper": 0.15, "foundation": 0.0, "foundationTerm": 0.0},
)

add_solana(
    name="getInflationRate", tag="Inflation",
    summary="Inflation rate",
    description="Returns the specific inflation values for the current epoch, including total inflation and the breakdown between validator rewards and foundation allocation.",
    params=[],
    params_example=[],
    result_schema=s_obj(properties=[
        ("total", s_num()), ("validator", s_num()), ("foundation", s_num()), ("epoch", s_int()),
    ]),
    result_example={"total": 0.0387, "validator": 0.0387, "foundation": 0.0, "epoch": 965},
)

add_solana(
    name="getInflationReward", tag="Inflation",
    summary="Inflation rewards",
    description="Returns the inflation/staking reward for a list of addresses for an epoch.",
    params=[
        {"name": "addresses", "schema_doc": "Array of base-58 pubkeys.", "schema": s_arr(s_string(desc="Pubkey of the staked account or vote account, base-58.", example="FbXMxhgoCYbZ4dWaCVzJWeFqW2tQ8sR82Hi8YyQrEaxR"), desc="Pubkeys to fetch inflation rewards for. Each pubkey returns one entry in the result array, in order."), "required": True},
        config_param(extra_props={"epoch": s_int(desc="Specific epoch to query. Omit to use the latest finalized epoch.", example=964)}),
    ],
    params_example=[["FbXMxhgoCYbZ4dWaCVzJWeFqW2tQ8sR82Hi8YyQrEaxR"], {"epoch": 964}],
    result_schema=s_arr(s_obj(nullable=True, properties=[
        ("epoch", s_int()), ("effectiveSlot", s_int()), ("amount", s_int()),
        ("postBalance", s_int()), ("commission", s_int(nullable=True)),
    ], desc="Reward object, or null if no reward for that address.")),
    result_example=[{"epoch": 964, "effectiveSlot": 416500000, "amount": 1234567, "postBalance": 99999999999, "commission": 5}],
)

# Supply
add_solana(
    name="getSupply", tag="Supply",
    summary="Total SOL supply",
    description="Returns information about the current supply of SOL on the Solana network.",
    params=[config_param(extra_props={"excludeNonCirculatingAccountsList": s_bool(desc="If true, omit the (potentially long) `nonCirculatingAccounts` list from the response. Default false.", example=True)})],
    params_example=[{"commitment": "finalized"}],
    result_schema=s_obj(required=["context", "value"], properties=[
        ("context", s_ref("#/components/schemas/Context")),
        ("value", s_obj(properties=[
            ("total", s_int()), ("circulating", s_int()), ("nonCirculating", s_int()),
            ("nonCirculatingAccounts", s_arr(s_string())),
        ])),
    ]),
    result_example={"context": {"slot": 416997240, "apiVersion": "3.1.10"}, "value": {"total": 625571106922491065, "circulating": 576208254345185897, "nonCirculating": 49362852577305168, "nonCirculatingAccounts": []}},
)

add_solana(
    name="getLargestAccounts", tag="Supply",
    summary="Largest SOL accounts",
    description="Returns the 20 largest accounts by lamport balance. Results may be cached up to two hours.",
    params=[config_param(extra_props={"filter": s_string(desc="Restrict the response to circulating or non-circulating accounts.", enum=["circulating", "nonCirculating"], example="circulating")})],
    params_example=[{"filter": "circulating"}],
    result_schema=s_obj(required=["context", "value"], properties=[
        ("context", s_ref("#/components/schemas/Context")),
        ("value", s_arr(s_obj(properties=[("address", s_string()), ("lamports", s_int())]))),
    ]),
    result_example={"context": {"slot": 416997240, "apiVersion": "3.1.10"}, "value": [{"address": "FbXMxhgoCYbZ4dWaCVzJWeFqW2tQ8sR82Hi8YyQrEaxR", "lamports": 99999999999}]},
)

# Misc
add_solana(
    name="requestAirdrop", tag="Misc",
    summary="Airdrop SOL (devnet/testnet only)",
    description="⚠️ WARNING: This RPC method is disabled on Solana Vibe Station mainnet-beta nodes. This method is not available on our infrastructure. Please use alternative faucets for obtaining devnet/testnet SOL: Solana Faucet QuickNode Multi-chain Faucet Solana CLI: solana airdrop 1 Requests an airdrop of lamports to a specified Pubkey.",
    params=[
        pubkey_param(),
        {"name": "lamports", "schema_doc": "Lamports to airdrop.", "schema": s_int(example=1000000000), "required": True},
        config_param(),
    ],
    params_example=["83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri", 1000000000, {"commitment": "finalized"}],
    result_schema=s_string(desc="Airdrop transaction signature, base-58."),
    result_example="4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa",
)

add_solana(
    name="minimumLedgerSlot", tag="Misc",
    summary="Lowest slot in ledger",
    description="Returns the lowest slot that the node has information about in its ledger. This method is useful for understanding the historical data availability of a Solana node. The value may increase over time if the node is configured to purge older ledger data to manage storage requirements. This is particularly important for applications that need to query historical data, as attempting to access slots below this minimum will result in data not being available. The method provides a simple way to determine the earliest point in time for which the node can provide blockchain state information.",
    params=[],
    params_example=[],
    result_schema=s_int(),
    result_example=349200000,
)

add_solana(
    name="getRecentPerformanceSamples", tag="Misc",
    summary="Recent performance samples",
    description="Returns a list of recent performance samples in reverse slot order (most recent first). Performance samples are collected every 60 seconds and provide detailed metrics about network activity including transaction counts, slot progression, and timing information. Each sample represents a 60-second window of network activity and includes: Total number of transactions processed Number of non-vote transactions (user-initiated transactions) Number of slots that occurred during the sample period The slot number when the sample was taken",
    params=[{"name": "limit", "schema_doc": "Number of samples to return (1–720).", "schema": s_int(example=5), "required": False}],
    params_example=[5],
    result_schema=s_arr(s_obj(properties=[
        ("slot", s_int()), ("numTransactions", s_int()), ("numSlots", s_int()),
        ("samplePeriodSecs", s_int()), ("numNonVoteTransactions", s_int()),
    ])),
    result_example=[{"slot": 416997380, "numTransactions": 168226, "numSlots": 152, "samplePeriodSecs": 60, "numNonVoteTransactions": 54837}, {"slot": 416997228, "numTransactions": 174204, "numSlots": 158, "samplePeriodSecs": 60, "numNonVoteTransactions": 56218}, {"slot": 416997070, "numTransactions": 167063, "numSlots": 145, "samplePeriodSecs": 60, "numNonVoteTransactions": 58812}],
)



add_solana(
    name="getFirstAvailableBlock", tag="Block",
    summary="Lowest available block in the ledger",
    description="Returns the slot of the lowest confirmed block that has not been purged from the ledger. This is useful for determining the earliest available block data in the ledger history.",
    params=[],
    params_example=[],
    result_schema=s_int(desc="Lowest slot the node has data for in its ledger.", example=140000000),
    result_example=140000000,
)

add_solana(
    name="getHighestSnapshotSlot", tag="Block",
    summary="Highest slots covered by snapshots",
    description="Returns the highest slot information that the node has snapshots for. This will find the highest full snapshot slot, and the highest incremental snapshot slot based on the full snapshot slot, if there is one. Version Restriction : This method is only available in solana-core v1.9 or newer. Please use getSnapshotSlot for solana-core v1.8 and below.",
    params=[],
    params_example=[],
    result_schema=s_obj(properties=[
        ("full", s_int(desc="Highest full snapshot slot the node has.", example=416997000)),
        ("incremental", s_int(nullable=True, desc="Highest incremental snapshot slot derived from the full snapshot, if any.", example=416997220)),
    ]),
    result_example={"full": 416997000, "incremental": 416997220},
)

add_solana(
    name="getMaxRetransmitSlot", tag="Slots",
    summary="Highest slot retransmitted",
    description="Returns the highest slot number for which the validator has retransmitted shreds from its retransmit stage.",
    params=[],
    params_example=[],
    result_schema=s_int(desc="Highest slot the retransmit stage has reached.", example=416997239),
    result_example=416997239,
)

add_solana(
    name="getMaxShredInsertSlot", tag="Slots",
    summary="Highest slot with shred insertion",
    description="Returns the highest slot number for which shreds have been received and inserted into the validator's blockstore.",
    params=[],
    params_example=[],
    result_schema=s_int(desc="Highest slot for which the node has inserted shreds.", example=416997239),
    result_example=416997239,
)


# ---------------------------------------------------------------------------
# HISTORICAL RPC method catalog.
# ---------------------------------------------------------------------------

HISTORICAL_METHODS = []


def add_historical(**method):
    HISTORICAL_METHODS.append(method)


add_historical(
    name="getBlock", tag="Block",
    summary="Historical block by slot",
    description="Returns identity and transaction information about a confirmed block in the ledger. Provides detailed block data including all transactions and their metadata.",
    params=[
        {"name": "slot", "schema_doc": "Slot number.", "schema": s_int(example=178000000), "required": True},
        config_param(extra_props={
            "encoding": s_ref("#/components/schemas/Encoding"),
            "transactionDetails": s_ref("#/components/schemas/TransactionDetails"),
            "rewards": s_bool(), "maxSupportedTransactionVersion": s_int(),
        }),
    ],
    params_example=[178000000, {"maxSupportedTransactionVersion": 0, "transactionDetails": "full"}],
    result_schema=s_obj(properties=[
        ("blockhash", s_string()), ("previousBlockhash", s_string()),
        ("parentSlot", s_int()), ("blockHeight", s_int()),
        ("blockTime", s_int(nullable=True)),
        ("transactions", s_arr(s_obj(additionalProperties=True))),
    ]),
    result_example={"blockhash": "3Eq21vXNB5s86c62bVuUfTeaMif1N2kUqRPBmGRJhyTA", "previousBlockhash": "mfcyqEXB3DnHXki6KjjmZck6YjmZLvpAByy2fj4nh6B", "parentSlot": 177999999, "blockHeight": 162345678, "blockTime": 1700000000, "transactions": []},
)

add_historical(
    name="getBlocks", tag="Block",
    summary="Historical confirmed blocks in a range",
    description="Returns a list of confirmed blocks between two slots",
    params=[
        {"name": "startSlot", "schema_doc": "Start slot (inclusive).", "schema": s_int(example=178000000), "required": True},
        {"name": "endSlot", "schema_doc": "End slot (inclusive).", "schema": s_int(example=178000010), "required": False},
        config_param(),
    ],
    params_example=[178000000, 178000010],
    result_schema=s_arr(s_int()),
    result_example=[178000000, 178000001, 178000004, 178000005, 178000010],
)

add_historical(
    name="getBlocksWithLimit", tag="Block",
    summary="Historical confirmed blocks starting at slot",
    description="Returns a list of confirmed blocks starting at the given slot. This method provides an efficient way to retrieve a range of sequential block slots, which is useful for block explorers, analytics tools, and applications that need to process historical blockchain data in batches. Important : The limit must be no more than 500,000 blocks higher than the start_slot.",
    params=[
        {"name": "startSlot", "schema_doc": "Start slot.", "schema": s_int(example=178000000), "required": True},
        {"name": "limit", "schema_doc": "Number of blocks (max 500,000).", "schema": s_int(example=10), "required": True},
        config_param(),
    ],
    params_example=[178000000, 10],
    result_schema=s_arr(s_int()),
    result_example=[178000000, 178000001, 178000004, 178000005, 178000010, 178000012, 178000014, 178000015, 178000016, 178000018],
)

add_historical(
    name="getBlockTime", tag="Block",
    summary="Historical block production time",
    description="Returns the estimated production time of a block. Each validator reports their UTC time to the ledger on a regular interval by intermittently adding a timestamp to a Vote for a particular block. A requested block's time is calculated from the stake-weighted mean of the Vote timestamps in a set of recent blocks recorded on the ledger.",
    params=[{"name": "slot", "schema_doc": "Slot number.", "schema": s_int(example=178000000), "required": True}],
    params_example=[178000000],
    result_schema=s_int(nullable=True),
    result_example=1700000000,
)

add_historical(
    name="getFirstAvailableBlock", tag="Block",
    summary="Lowest historical block",
    description="Returns the slot of the lowest confirmed block that has not been purged from the ledger. This is useful for determining the earliest available block data in the ledger history.",
    params=[],
    params_example=[],
    result_schema=s_int(),
    result_example=140000000,
)

add_historical(
    name="getSlot", tag="Slots",
    summary="Highest historical slot",
    description="Returns the highest slot available on the historical RPC endpoints.",
    params=[config_param()],
    params_example=[{"commitment": "finalized"}],
    result_schema=s_int(),
    result_example=416990000,
)

add_historical(
    name="getSignaturesForAddress", tag="Transactions",
    summary="Historical signatures for an address",
    description="Returns signatures for confirmed transactions that include the given address in their accountKeys list. Returns signatures backwards in time from the provided signature or most recent confirmed block. This method is essential for transaction history, wallet activity feeds, and building transaction explorers.",
    params=[
        pubkey_param(),
        config_param(extra_props=OrderedDict([
            ("limit", s_int(desc="Maximum number of signatures to return (1–1000).", example=10, minimum=1, maximum=1000)),
            ("before", s_string(desc="Start the search before this signature (exclusive).", example="4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa")),
            ("until", s_string(desc="Search until this signature (inclusive).", example="4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa")),
        ])),
    ],
    params_example=["83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri", {"limit": 10}],
    result_schema=s_arr(s_obj(properties=[
        ("signature", s_string()), ("slot", s_int()),
        ("err", s_obj(nullable=True, additionalProperties=True)),
        ("memo", s_string(nullable=True)), ("blockTime", s_int(nullable=True)),
        ("confirmationStatus", s_string(enum=["finalized"])),
    ])),
    result_example=[{"signature": "4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa", "slot": 178000000, "err": None, "memo": None, "blockTime": 1700000000, "confirmationStatus": "finalized"}],
)

add_historical(
    name="getSignatureStatuses", tag="Transactions",
    summary="Historical signature statuses",
    description="Returns the statuses of a list of transaction signatures. This method is essential for checking whether transactions have been confirmed, failed, or are still processing. It's commonly used by wallets and dApps to monitor transaction status and provide real-time feedback to users. You can check up to 256 signatures in a single request.",
    params=[
        {"name": "signatures", "schema_doc": "Array of base-58 signatures.", "schema": s_arr(s_string()), "required": True},
        config_param(extra_props={"searchTransactionHistory": s_bool(desc="If true, look up signatures in the long-term ledger archive (always true for the historical RPC).", example=True, default=True)}),
    ],
    params_example=[["4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa"], {"searchTransactionHistory": True}],
    result_schema=s_obj(required=["context", "value"], properties=[
        ("context", s_ref("#/components/schemas/Context")),
        ("value", s_arr(s_obj(nullable=True, properties={
            "slot": s_int(), "confirmations": s_int(nullable=True),
            "err": s_obj(nullable=True, additionalProperties=True),
            "confirmationStatus": s_string(enum=["finalized"]),
        }, desc="Status object, or null if signature is unknown."))),
    ]),
    result_example={"context": {"slot": 416997240, "apiVersion": "3.1.10"}, "value": [{"slot": 178000000, "confirmations": None, "err": None, "confirmationStatus": "finalized"}]},
)

add_historical(
    name="getTransaction", tag="Transactions",
    summary="Historical transaction by signature",
    description="Returns transaction details for a confirmed transaction signature. Provides comprehensive information about the transaction including its status, fees, logs, and account changes. This method is essential for transaction explorers, wallets, and dApps that need to analyze transaction execution details. Important : For most modern Solana transactions, you must include maxSupportedTransactionVersion: 0 in the request parameters, otherwise the request will fail with an error if the transaction is a versioned transaction.",
    params=[
        {"name": "signature", "schema_doc": "Base-58 transaction signature.", "schema": s_string(), "required": True},
        config_param(extra_props={"encoding": s_ref("#/components/schemas/Encoding"), "maxSupportedTransactionVersion": s_int()}),
    ],
    params_example=["4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa", {"maxSupportedTransactionVersion": 0}],
    result_schema=s_obj(nullable=True, properties=[
        ("slot", s_int()), ("blockTime", s_int(nullable=True)),
        ("transaction", s_obj(additionalProperties=True)),
        ("meta", s_obj(additionalProperties=True, nullable=True)),
        ("version", _OD([("oneOf", [s_int(), s_string()])])),
    ]),
    result_example={"slot": 178000000, "blockTime": 1700000000, "transaction": {"signatures": ["..."], "message": {}}, "meta": {"err": None, "fee": 5000, "preBalances": [1000000], "postBalances": [995000]}, "version": 0},
)




add_historical(
    name="getTransactionsForAddress", tag="Transactions",
    summary="Filtered transaction history for an address",
    description=(
        "Enhanced transaction history API with powerful filtering, sorting, and "
        "pagination capabilities for retrieving comprehensive transaction data for "
        "any address. Supports bidirectional sorting, time/slot/status filtering, "
        "and efficient keyset pagination via the `paginationToken` cursor.\n\n"
        "**Note:** SVS supports the same parameter shape as the upstream provider "
        "with one exception — the `filters.tokenAccounts` field is **not supported** "
        "on Solana Vibe Station. All other filters (`slot`, `blockTime`, `signature`, "
        "`status`) work as documented."
    ),
    params=[
        {
            "name": "address",
            "schema_doc": "Solana account address whose transaction history to retrieve. May be a wallet, token mint, program, NFT, etc.",
            "schema": s_string(
                desc="Solana account address, base-58.",
                example="Vote111111111111111111111111111111111111111",
            ),
            "required": True,
        },
        {
            "name": "config",
            "schema_doc": "Optional configuration controlling sort order, pagination, transaction detail level, and filters.",
            "required": False,
            "schema": s_obj(
                desc="Optional configuration object for filtering, sorting, and pagination.",
                properties=OrderedDict([
                    ("transactionDetails", s_string(
                        desc="Level of transaction detail to return.",
                        enum=["signatures", "full"],
                        default="signatures",
                        example="signatures",
                    )),
                    ("sortOrder", s_string(
                        desc="Result ordering by slot. `desc` returns newest first.",
                        enum=["desc", "asc"],
                        default="desc",
                        example="desc",
                    )),
                    ("commitment", s_ref("#/components/schemas/Commitment")),
                    ("limit", s_int(
                        desc="Max records to return. 1-1000 when transactionDetails is `signatures`; 1-100 when `full`.",
                        example=10,
                        minimum=1,
                        maximum=1000,
                    )),
                    ("paginationToken", s_string(
                        desc="Keyset pagination cursor in `slot:position` format. Pass the value returned in the previous response's `paginationToken` to fetch the next page.",
                        example="1055:5",
                    )),
                    ("encoding", s_ref("#/components/schemas/Encoding")),
                    ("maxSupportedTransactionVersion", s_int(
                        desc="Highest transaction version the client can handle. Only meaningful when `transactionDetails` is `full`. Set to 0 to include versioned transactions.",
                        example=0,
                    )),
                    ("filters", s_obj(
                        desc=(
                            "Optional set of filters narrowing the result set. Filters intersect "
                            "(AND-combined). **NOTE:** `filters.tokenAccounts` is NOT supported on "
                            "SVS — it is silently ignored or rejected. All other filters below are "
                            "fully supported."
                        ),
                        properties=OrderedDict([
                            ("slot", s_obj(
                                desc="Slot range filter. Combine fields for half-open or closed ranges.",
                                properties=OrderedDict([
                                    ("gte", s_int(desc="Match slots >= this value.", example=400000000)),
                                    ("gt",  s_int(desc="Match slots > this value.")),
                                    ("lte", s_int(desc="Match slots <= this value.")),
                                    ("lt",  s_int(desc="Match slots < this value.")),
                                ]),
                            )),
                            ("blockTime", s_obj(
                                desc="Unix-time (seconds) range filter on block production time.",
                                properties=OrderedDict([
                                    ("gte", s_int(desc="Match block times >= this Unix timestamp.", example=1700000000)),
                                    ("gt",  s_int(desc="Match block times > this Unix timestamp.")),
                                    ("lte", s_int(desc="Match block times <= this Unix timestamp.")),
                                    ("lt",  s_int(desc="Match block times < this Unix timestamp.")),
                                    ("eq",  s_int(desc="Match block times exactly equal to this Unix timestamp.")),
                                ]),
                            )),
                            ("signature", s_obj(
                                desc="Signature range filter (lexicographic ordering of base-58 strings).",
                                properties=OrderedDict([
                                    ("gte", s_string(desc="Match signatures >= this value (lex order).")),
                                    ("gt",  s_string(desc="Match signatures > this value (lex order).")),
                                    ("lte", s_string(desc="Match signatures <= this value (lex order).")),
                                    ("lt",  s_string(desc="Match signatures < this value (lex order).")),
                                ]),
                            )),
                            ("status", s_string(
                                desc="Restrict to successful or failed transactions only.",
                                enum=["success", "failed"],
                                example="success",
                            )),
                        ]),
                    )),
                ]),
            ),
        },
    ],
    params_example=["Vote111111111111111111111111111111111111111", {"transactionDetails": "signatures", "limit": 10}],
    result_schema=s_obj(
        required=["data"],
        properties=[
            ("data", s_arr(
                s_obj(
                    required=["signature", "slot", "transactionIndex", "err", "blockTime", "confirmationStatus"],
                    properties=[
                        ("signature", s_string(desc="Transaction signature, base-58.", example="5h6xBEauJ3PK6SWCZ1PGjBvj8vDdWG3KpwATGy1ARAXFSDwt8GFXM7W5Ncn16wmqokgpiKRLuS83KUxyZyv2sUYv")),
                        ("slot", s_int(desc="Slot in which the transaction was confirmed.", example=1054)),
                        ("transactionIndex", s_int(desc="Position of the transaction within its block.", example=42)),
                        ("err", s_obj(nullable=True, additionalProperties=True, desc="Error object if the transaction failed; null if it succeeded.")),
                        ("memo", s_string(nullable=True, desc="Memo attached to the transaction, if any.")),
                        ("blockTime", s_int(nullable=True, desc="Estimated production time of the block, in Unix seconds.", example=1641038400)),
                        ("confirmationStatus", s_string(
                            desc="Cluster commitment level when the transaction was confirmed.",
                            enum=["processed", "confirmed", "finalized"],
                            example="finalized",
                        )),
                    ],
                ),
                desc="Transaction history records, ordered per `sortOrder`.",
            )),
            ("paginationToken", s_string(
                desc="Cursor for the next page in `slot:position` format, or null/missing when there are no more results.",
                example="1055:5",
            )),
        ],
    ),
    result_example={
        "data": [{
            "signature": "5h6xBEauJ3PK6SWCZ1PGjBvj8vDdWG3KpwATGy1ARAXFSDwt8GFXM7W5Ncn16wmqokgpiKRLuS83KUxyZyv2sUYv",
            "slot": 1054,
            "transactionIndex": 42,
            "err": None,
            "memo": None,
            "blockTime": 1641038400,
            "confirmationStatus": "finalized",
        }],
        "paginationToken": "1055:5",
    },
)

# ---------------------------------------------------------------------------
# WEBSOCKET RPC method catalog.
#
# These are JSON-RPC methods invoked over a WebSocket connection (wss://
# scheme). The spec documents each method as if it were a POST so that
# GitBook's OpenAPI rendering still produces a navigable per-method page
# with a request/response schema. Each operation's description notes that
# the actual transport is WebSocket and that the connection URL is wss://
# rather than https://.
#
# Subscribe methods return an integer subscription id. The server then
# pushes notifications to the client over the same WebSocket; those
# notifications are not modeled in OpenAPI (event streams are out of
# scope for OpenAPI 3.0 — see the description for the message shape).
# Unsubscribe methods take that id and return a boolean.
# ---------------------------------------------------------------------------

WEBSOCKET_METHODS = []


def add_ws(**method):
    WEBSOCKET_METHODS.append(method)


# Subscription-id result schema (used by every *Subscribe method)
def _sub_id_result():
    return s_int(desc="Subscription id. Save this value to call the matching unsubscribe method later.", example=24040)


def _unsub_result():
    return s_bool(desc="True if the unsubscribe succeeded.", example=True)


# --- account subscriptions ---
add_ws(
    name="accountSubscribe", tag="Account Subscriptions",
    summary="Subscribe to account changes",
    description="Subscribe to an account to receive notifications when the lamports or data for a given account public key changes. Returns a subscription ID that can be used to unsubscribe. This method establishes a persistent WebSocket connection that will send real-time notifications whenever the specified account's state changes on the blockchain.",
    params=[
        pubkey_param(),
        config_param(extra_props={"encoding": s_ref("#/components/schemas/Encoding")}),
    ],
    params_example=["83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri", {"encoding": "jsonParsed", "commitment": "finalized"}],
    result_schema=_sub_id_result(),
    result_example=24040,
)

add_ws(
    name="accountUnsubscribe", tag="Account Subscriptions",
    summary="Cancel an account subscription",
    description="Unsubscribe from account change notifications. This method cancels an existing account subscription identified by the subscription ID that was returned from a previous accountSubscribe call. Once unsubscribed, you will no longer receive accountNotification messages for the specified subscription.",
    params=[
        {"name": "subscriptionId", "schema_doc": "Subscription id returned by accountSubscribe.",
         "schema": s_int(desc="Subscription id.", example=24040), "required": True},
    ],
    params_example=[24040],
    result_schema=_unsub_result(),
    result_example=True,
)

# --- block subscriptions (unsupported) ---
add_ws(
    name="blockSubscribe", tag="Block Subscriptions",
    summary="Subscribe to new blocks (UNSUPPORTED on SVS)",
    description="**Not available on SVS nodes.** This method is considered unstable in Agave/Solana and is therefore not enabled on our RPC infrastructure. Calls will be rejected. Use an alternative subscription method or polling-based pattern for this use case. Subscribe to receive notification anytime a new block is confirmed or finalized.",
    params=[
        {"name": "filter", "schema_doc": "Filter for block subscription (`all`, or {mentionsAccountOrProgram: <pubkey>}).",
         "schema": s_obj(additionalProperties=True, desc="Subscription filter."), "required": True},
        config_param(extra_props={
            "encoding": s_ref("#/components/schemas/Encoding"),
            "transactionDetails": s_ref("#/components/schemas/TransactionDetails"),
            "showRewards": s_bool(desc="Include block-level rewards.", example=False),
            "maxSupportedTransactionVersion": s_int(desc="Highest transaction version the client can handle.", example=0),
        }),
    ],
    params_example=["all", {"encoding": "json", "showRewards": False, "transactionDetails": "full", "maxSupportedTransactionVersion": 0}],
    result_schema=_sub_id_result(),
    result_example=24040,
)

add_ws(
    name="blockUnsubscribe", tag="Block Subscriptions",
    summary="Cancel a block subscription (UNSUPPORTED on SVS)",
    description="**Not available on SVS nodes.** This method is considered unstable in Agave/Solana and is therefore not enabled on our RPC infrastructure. Calls will be rejected. Use an alternative subscription method or polling-based pattern for this use case. Unsubscribe from block notifications.",
    params=[
        {"name": "subscriptionId", "schema_doc": "Subscription id returned by blockSubscribe.",
         "schema": s_int(desc="Subscription id.", example=24040), "required": True},
    ],
    params_example=[24040],
    result_schema=_unsub_result(),
    result_example=True,
)

# --- logs subscriptions ---
add_ws(
    name="logsSubscribe", tag="Logs Subscriptions",
    summary="Subscribe to transaction logs",
    description="Subscribe to transaction logging to receive notifications when transactions occur that match specified filter criteria. This method establishes a persistent WebSocket connection that will send real-time log notifications whenever transactions matching your filters are processed by the network. You can filter by all transactions, transactions with votes, or transactions mentioning specific accounts.",
    params=[
        {
            "name": "filter",
            "schema_doc": "Either the string `all`, the string `allWithVotes`, or {mentions: [<pubkey>]}.",
            "schema": s_obj(additionalProperties=True, desc="Logs filter — string `all` / `allWithVotes`, or an object with `mentions: [pubkey]`."),
            "required": True,
        },
        config_param(),
    ],
    params_example=[{"mentions": ["11111111111111111111111111111111"]}, {"commitment": "finalized"}],
    result_schema=_sub_id_result(),
    result_example=24040,
)

add_ws(
    name="logsUnsubscribe", tag="Logs Subscriptions",
    summary="Cancel a logs subscription",
    description="Unsubscribe from transaction log notifications. This method cancels an existing logs subscription identified by the subscription ID that was returned from a previous logsSubscribe call. Once unsubscribed, you will no longer receive logsNotification messages for the specified subscription.",
    params=[
        {"name": "subscriptionId", "schema_doc": "Subscription id returned by logsSubscribe.",
         "schema": s_int(desc="Subscription id.", example=24040), "required": True},
    ],
    params_example=[24040],
    result_schema=_unsub_result(),
    result_example=True,
)

# --- program subscriptions ---
add_ws(
    name="programSubscribe", tag="Program Subscriptions",
    summary="Subscribe to program-owned account changes",
    description="Subscribe to a program to receive notifications when the lamports or data for an account owned by the given program changes. This method establishes a persistent WebSocket connection that will send real-time notifications whenever accounts owned by the specified program are created, modified, or deleted. You can filter results by data size, account owner, or custom criteria to only receive notifications for accounts that match your requirements.",
    params=[
        pubkey_param(name="programId", desc="Program pubkey, base-58."),
        config_param(extra_props={
            "encoding": s_ref("#/components/schemas/Encoding"),
            "filters": s_arr(memcmp_filter_schema(), desc="Optional filters that narrow the account set."),
        }),
    ],
    params_example=["TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq", {"encoding": "jsonParsed", "filters": [{"dataSize": 165}]}],
    result_schema=_sub_id_result(),
    result_example=24040,
)

add_ws(
    name="programUnsubscribe", tag="Program Subscriptions",
    summary="Cancel a program subscription",
    description="Unsubscribe from program-owned account change notifications. This method cancels an existing program subscription identified by the subscription ID that was returned from a previous programSubscribe call. Once unsubscribed, you will no longer receive programNotification messages for accounts owned by the specified program.",
    params=[
        {"name": "subscriptionId", "schema_doc": "Subscription id returned by programSubscribe.",
         "schema": s_int(desc="Subscription id.", example=24040), "required": True},
    ],
    params_example=[24040],
    result_schema=_unsub_result(),
    result_example=True,
)

# --- root subscriptions ---
add_ws(
    name="rootSubscribe", tag="Root Subscriptions",
    summary="Subscribe to root slot updates",
    description="Subscribe to receive notification anytime a new root is set by the validator. This method establishes a persistent WebSocket connection that will send real-time notifications whenever the validator updates the root slot. The root represents the most recent slot that has been finalized and committed to the ledger. This subscription is useful for tracking the overall progress of the blockchain and understanding when transactions become irreversibly confirmed.",
    params=[],
    params_example=[],
    result_schema=_sub_id_result(),
    result_example=24040,
)

add_ws(
    name="rootUnsubscribe", tag="Root Subscriptions",
    summary="Cancel a root subscription",
    description="Unsubscribe from root notifications. This method cancels an existing root subscription identified by the subscription ID that was returned from a previous rootSubscribe call. Once unsubscribed, you will no longer receive rootNotification messages when the validator sets new root slots.",
    params=[
        {"name": "subscriptionId", "schema_doc": "Subscription id returned by rootSubscribe.",
         "schema": s_int(desc="Subscription id.", example=24040), "required": True},
    ],
    params_example=[24040],
    result_schema=_unsub_result(),
    result_example=True,
)

# --- signature subscriptions ---
add_ws(
    name="signatureSubscribe", tag="Signature Subscriptions",
    summary="Subscribe to a transaction signature's status",
    description="Subscribe to receive a notification when the transaction with the given signature reaches the specified commitment level. This is a subscription to a single notification that is automatically cancelled by the server once the signatureNotification is sent. Optionally, you can also receive notifications when the signature is first received by the RPC before processing begins. The transaction signature must be the first signature from the transaction.",
    params=[
        {"name": "signature", "schema_doc": "Base-58 transaction signature.",
         "schema": s_string(desc="Transaction signature.", example="4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa"),
         "required": True},
        config_param(extra_props={"enableReceivedNotification": s_bool(desc="Also send a notification when the transaction is first received.", example=False)}),
    ],
    params_example=["4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa", {"commitment": "finalized"}],
    result_schema=_sub_id_result(),
    result_example=24040,
)

add_ws(
    name="signatureUnsubscribe", tag="Signature Subscriptions",
    summary="Cancel a signature subscription",
    description="Unsubscribe from signature confirmation notification. This method cancels an existing signature subscription identified by the subscription ID that was returned from a previous signatureSubscribe call. Note that signature subscriptions are automatically cancelled by the server after sending the first notification, so this method is typically used to cancel a subscription before the transaction is confirmed or processed.",
    params=[
        {"name": "subscriptionId", "schema_doc": "Subscription id returned by signatureSubscribe.",
         "schema": s_int(desc="Subscription id.", example=24040), "required": True},
    ],
    params_example=[24040],
    result_schema=_unsub_result(),
    result_example=True,
)

# --- slot subscriptions ---
add_ws(
    name="slotSubscribe", tag="Slot Subscriptions",
    summary="Subscribe to slot updates",
    description="Subscribe to receive notification anytime a slot is processed by the validator. This method establishes a persistent WebSocket connection that will send real-time notifications whenever the validator processes a new slot. Each notification includes information about the current slot, its parent slot, and the current root slot. This subscription provides high-frequency updates about blockchain progression and is useful for monitoring network activity, tracking slot timing, and understanding the relationship between processed slots and finalized roots.",
    params=[],
    params_example=[],
    result_schema=_sub_id_result(),
    result_example=24040,
)

add_ws(
    name="slotUnsubscribe", tag="Slot Subscriptions",
    summary="Cancel a slot subscription",
    description="Unsubscribe from slot notifications. This method cancels an existing slot subscription identified by the subscription ID that was returned from a previous slotSubscribe call. Once unsubscribed, you will no longer receive slotNotification messages when new slots are processed by the validator. This is useful for stopping high-frequency slot monitoring when no longer needed.",
    params=[
        {"name": "subscriptionId", "schema_doc": "Subscription id returned by slotSubscribe.",
         "schema": s_int(desc="Subscription id.", example=24040), "required": True},
    ],
    params_example=[24040],
    result_schema=_unsub_result(),
    result_example=True,
)

# --- vote subscriptions (unsupported) ---
add_ws(
    name="voteSubscribe", tag="Vote Subscriptions",
    summary="Subscribe to vote messages (UNSUPPORTED on SVS)",
    description="**Not available on SVS nodes.** This method is considered unstable in Agave/Solana and is therefore not enabled on our RPC infrastructure. Calls will be rejected. Use an alternative subscription method or polling-based pattern for this use case. Subscribe to receive notification any time a new vote is observed in gossip.",
    params=[],
    params_example=[],
    result_schema=_sub_id_result(),
    result_example=24040,
)

add_ws(
    name="voteUnsubscribe", tag="Vote Subscriptions",
    summary="Cancel a vote subscription (UNSUPPORTED on SVS)",
    description="**Not available on SVS nodes.** This method is considered unstable in Agave/Solana and is therefore not enabled on our RPC infrastructure. Calls will be rejected. Use an alternative subscription method or polling-based pattern for this use case. Unsubscribe from vote notifications.",
    params=[
        {"name": "subscriptionId", "schema_doc": "Subscription id returned by voteSubscribe.",
         "schema": s_int(desc="Subscription id.", example=24040), "required": True},
    ],
    params_example=[24040],
    result_schema=_unsub_result(),
    result_example=True,
)


WEBSOCKET_SERVERS = [
    {"url": "wss://public.rpc.solanavibestation.com",  "description": "Public WebSocket endpoint (rate-limited)"},
    {"url": "wss://lite.rpc.solanavibestation.com",    "description": "Lite tier WebSocket"},
    {"url": "wss://basic.rpc.solanavibestation.com",   "description": "Basic tier WebSocket"},
    {"url": "wss://ultra.rpc.solanavibestation.com",   "description": "Ultra tier WebSocket"},
    {"url": "wss://elite.rpc.solanavibestation.com",   "description": "Elite tier WebSocket"},
    {"url": "wss://epic.rpc.solanavibestation.com",    "description": "Epic tier WebSocket"},
]

WEBSOCKET_TAGS = [
    {"name": "Account Subscriptions",   "description": "Subscribe to changes to a single account."},
    {"name": "Block Subscriptions",     "description": "Subscribe to new blocks (currently unsupported on SVS)."},
    {"name": "Logs Subscriptions",      "description": "Subscribe to transaction log lines."},
    {"name": "Program Subscriptions",   "description": "Subscribe to changes to all accounts owned by a program."},
    {"name": "Root Subscriptions",      "description": "Subscribe to root slot updates from the leader."},
    {"name": "Signature Subscriptions", "description": "Subscribe to a single transaction signature's confirmation."},
    {"name": "Slot Subscriptions",      "description": "Subscribe to slot processed/confirmed/rooted notifications."},
    {"name": "Vote Subscriptions",      "description": "Subscribe to gossip votes (currently unsupported on SVS)."},
]



def build_historical_consolidated(methods):
    """Build a single POST /historical operation that documents every
    historical RPC method via a multi-example request body and a generic
    JSON-RPC response envelope.

    OpenAPI 3.0 requires each (path, verb) pair to be unique, so we can't
    have N separate operations all at POST /historical. The historical
    archive lives at exactly that path on every SVS server, with the
    method passed in the JSON-RPC body. To document every method while
    honoring that constraint, we emit ONE operation and use the
    `examples:` map (which GitBook renders as a Test-It dropdown) to
    show the request body for each method. Per-method response examples
    are listed in the description as a method-by-method reference.
    """
    method_names = [m["name"] for m in methods]

    request_schema = _OD([
        ("type", "object"),
        ("required", ["jsonrpc", "id", "method", "params"]),
        ("properties", _OD([
            ("jsonrpc", _OD([
                ("type", "string"), ("enum", ["2.0"]),
                ("description", "JSON-RPC protocol version."), ("example", "2.0"),
            ])),
            ("id", _OD([
                ("oneOf", [_OD([("type", "string")]), _OD([("type", "integer")])]),
                ("description", "Request identifier echoed back in the response."),
                ("example", 1),
            ])),
            ("method", _OD([
                ("type", "string"),
                ("enum", method_names),
                ("description", "The historical RPC method to call. Each value below corresponds to a documented method; pick the one matching your request body."),
                ("example", method_names[0] if method_names else "getBlock"),
            ])),
            ("params", _OD([
                ("type", "array"),
                ("description", "Positional parameters for the chosen method. The shape varies per method; see the Test-It examples below for one-click presets."),
            ])),
        ])),
    ])

    # Build the named-examples map.
    examples = _OD()
    for m in methods:
        name = m["name"]
        examples[name] = _OD([
            ("summary", f"{name} — {m['summary']}"),
            ("value", _OD([
                ("jsonrpc", "2.0"),
                ("id", 1),
                ("method", name),
                ("params", m["params_example"]),
            ])),
        ])

    # Build a markdown method index for the description.
    method_index = ["", "## Methods supported", ""]
    for m in methods:
        first_line = m["description"].split("\n", 1)[0].strip()
        method_index.append(f"- **`{m['name']}`** — {first_line}")
    method_index.append("")

    description = (
        "All historical methods POST to **`/historical`** on the chosen SVS server. "
        "The method name is passed in the JSON-RPC request body, exactly like the main "
        "Solana RPC. Use the Test-It dropdown to pick a method; each named example "
        "below populates the request body for that method.\n"
        + "\n".join(method_index)
    )

    # Generic JSON-RPC response envelope. The shape of `result` varies per
    # method (and is documented in each per-method's full description above).
    response_schema = _OD([
        ("allOf", [
            _OD([("$ref", "#/components/schemas/JsonRpcEnvelope")]),
            _OD([
                ("type", "object"),
                ("required", ["result"]),
                ("properties", _OD([
                    ("result", _OD([
                        ("description", "Method-specific result. See each method's documentation for the shape."),
                        ("oneOf", [
                            _OD([("type", "object"), ("additionalProperties", True)]),
                            _OD([("type", "array"), ("items", _OD([("type", "object"), ("additionalProperties", True)]))]),
                            _OD([("type", "integer")]),
                            _OD([("type", "string")]),
                            _OD([("type", "boolean")]),
                        ]),
                    ])),
                ])),
            ]),
        ]),
    ])

    response_examples = _OD()
    for m in methods:
        response_examples[m["name"]] = _OD([
            ("summary", f"Successful {m['name']} response"),
            ("value", _OD([
                ("jsonrpc", "2.0"),
                ("id", 1),
                ("result", m["result_example"]),
            ])),
        ])

    # Code samples: derive from the FIRST method's params_example so the
    # tabbed code samples have a runnable cURL/Python/JS/Rust against
    # /historical. The generic `historical_code_samples_for` already
    # POSTs to /historical correctly.
    first = methods[0]
    x_samples = code_samples.historical_code_samples_for(first["name"], first["params_example"])

    op = _OD([
        ("operationId", "historicalRpc"),
        ("summary", "Historical Solana JSON-RPC"),
        ("tags", ["Historical RPC"]),
        ("description", description),
        ("requestBody", _OD([
            ("required", True),
            ("content", _OD([
                ("application/json", _OD([
                    ("schema", request_schema),
                    ("examples", examples),
                ])),
            ])),
        ])),
        ("responses", _OD([
            ("200", _OD([
                ("description", "Successful JSON-RPC response. Result shape depends on the method."),
                ("content", _OD([
                    ("application/json", _OD([
                        ("schema", response_schema),
                        ("examples", response_examples),
                    ])),
                ])),
            ])),
        ])),
        ("security", SECURITY),
        ("x-codeSamples", [
            _OD([("lang", s["lang"]), ("label", s["label"]), ("source", s["source"])])
            for s in x_samples
        ]),
    ])
    for code, body in STANDARD_RESPONSES.items():
        op["responses"][code] = body

    return _OD([("/historical", _OD([("post", op)]))])


# ---------------------------------------------------------------------------
# Spec assembly + emit.
# ---------------------------------------------------------------------------

SOLANA_SERVERS = [
    {"url": "https://public.rpc.solanavibestation.com", "description": "Public endpoint (rate-limited, no auth)"},
    {"url": "https://lite.rpc.solanavibestation.com",   "description": "Lite tier"},
    {"url": "https://basic.rpc.solanavibestation.com",  "description": "Basic tier"},
    {"url": "https://ultra.rpc.solanavibestation.com",  "description": "Ultra tier"},
    {"url": "https://elite.rpc.solanavibestation.com",  "description": "Elite tier"},
    {"url": "https://epic.rpc.solanavibestation.com",   "description": "Epic tier"},
    {"url": "https://basic.swqos.solanavibestation.com",  "description": "Basic tier with Stake-Weighted QoS"},
    {"url": "https://ultra.swqos.solanavibestation.com",  "description": "Ultra tier with Stake-Weighted QoS"},
    {"url": "https://elite.swqos.solanavibestation.com",  "description": "Elite tier with Stake-Weighted QoS"},
]

HISTORICAL_SERVERS = [
    {"url": "https://public.rpc.solanavibestation.com",  "description": "Public endpoint (rate-limited, no auth)"},
    {"url": "https://basic.rpc.solanavibestation.com",   "description": "Basic tier"},
    {"url": "https://ultra.rpc.solanavibestation.com",   "description": "Ultra tier"},
    {"url": "https://elite.rpc.solanavibestation.com",   "description": "Elite tier"},
    {"url": "https://epic.rpc.solanavibestation.com",    "description": "Epic tier"},
]

SOLANA_TAGS = [
    {"name": "Account",      "description": "Account state, balances, and SPL token accounts."},
    {"name": "Block",        "description": "Block production, lookups, and timing."},
    {"name": "Cluster",      "description": "Cluster topology, epoch info, and node identity."},
    {"name": "Fees",         "description": "Blockhash, fee estimation, and prioritization fees."},
    {"name": "Transactions", "description": "Submission, simulation, and lookup of transactions."},
    {"name": "Slots",        "description": "Current slot, slot leaders, and leader schedule."},
    {"name": "Stake",        "description": "Stake account utilities."},
    {"name": "Validators",   "description": "Vote accounts and validator status."},
    {"name": "Inflation",    "description": "Inflation governor, rate, and rewards."},
    {"name": "Supply",       "description": "Total SOL supply and largest accounts."},
    {"name": "Misc",         "description": "Airdrops, performance samples, and miscellany."},
]

HISTORICAL_TAGS = [
    {"name": "Block",        "description": "Historical block lookups."},
    {"name": "Transactions", "description": "Historical transactions and signatures."},
    {"name": "Slots",        "description": "Historical slot range."},
]


def assemble_spec(*, title, description, version, servers, tags, paths):
    return _OD([
        ("openapi", "3.0.3"),
        ("info", _OD([
            ("title", title),
            ("description", description),
            ("version", version),
            ("contact", _OD([("name", "Solana Vibe Station"), ("url", "https://www.solanavibestation.com")])),
            ("license", _OD([("name", "MIT OR Apache-2.0"), ("url", "https://opensource.org/licenses/MIT")])),
        ])),
        ("servers", servers),
        ("tags", tags),
        ("paths", paths),
        ("components", COMMON_COMPONENTS),
        ("security", SECURITY),
    ])


def main(out_dir):
    solana_paths = build_paths(SOLANA_METHODS, base_path_prefix="", base_note=ENDPOINT_NOTE)
    # Historical methods all live at the single path /historical on the
    # SVS server. OpenAPI 3.0 requires unique (path, verb) keys, so we
    # use a fragment-based path key per method: `/historical#getBlock`,
    # `/historical#getBlocks`, etc. The fragment is part of the path
    # KEY in the spec but is stripped by every HTTP client before the
    # request is sent (fragments are RFC 3986 client-side identifiers).
    # Net effect: each method is its own embeddable OpenAPI operation,
    # the actual HTTP request goes to POST /historical, and the per-
    # method discriminator is the JSON-RPC `method` field in the body.
    historical_paths = build_paths(HISTORICAL_METHODS, base_path_prefix="/historical#", base_note=HISTORICAL_ENDPOINT_NOTE, historical=True)

    solana_spec = assemble_spec(
        title="Solana Vibe Station RPC",
        description=textwrap.dedent("""\
            Solana JSON-RPC 2.0 endpoints hosted by Solana Vibe Station.

            Each method is documented as its own OpenAPI operation. In production all
            requests POST to the **root path** (`/`) of the chosen server URL — the
            method shown in the path (e.g. `/getBalance`) is a documentation grouping
            so each operation can be embedded individually in the docs.
        """),
        version="2.0.0", servers=SOLANA_SERVERS, tags=SOLANA_TAGS, paths=solana_paths,
    )

    historical_spec = assemble_spec(
        title="Solana Vibe Station Historical RPC",
        description=textwrap.dedent("""\
            Historical Solana JSON-RPC 2.0 methods hosted by Solana Vibe Station,
            served from long-term ledger storage.

            **Every historical method POSTs to the same path: `/historical`.**
            The method name is passed in the JSON-RPC request body exactly
            like the main Solana RPC.

            The path keys you see below (e.g. `/historical#getBlock`) include
            an OpenAPI fragment so each method renders as its own embeddable
            operation page. **The fragment is documentation-only — every
            HTTP client strips fragments before sending, so the actual
            request goes to `POST /historical` regardless of which page
            you copy the example from.**
        """),
        version="1.0.0", servers=HISTORICAL_SERVERS, tags=HISTORICAL_TAGS, paths=historical_paths,
    )

    with open(f"{out_dir}/solana-rpc.yaml", "w") as f:
        f.write("# Generated by scripts/generate-rpc-specs.py — edit the generator, not this file.\n")
        yaml.dump(solana_spec, f, sort_keys=False, allow_unicode=True, width=10000)

    with open(f"{out_dir}/historical-rpc.yaml", "w") as f:
        f.write("# Generated by scripts/generate-rpc-specs.py — edit the generator, not this file.\n")
        yaml.dump(historical_spec, f, sort_keys=False, allow_unicode=True, width=10000)

    print(f"Wrote solana-rpc.yaml ({len(SOLANA_METHODS)} methods)")
    print(f"Wrote historical-rpc.yaml ({len(HISTORICAL_METHODS)} methods)")

    websocket_paths = build_paths(WEBSOCKET_METHODS, base_path_prefix="", base_note=ENDPOINT_NOTE, websocket=True)

    websocket_spec = assemble_spec(
        title="Solana Vibe Station WebSocket RPC",
        description=textwrap.dedent("""\
            Solana JSON-RPC 2.0 methods invoked over a WebSocket connection.

            Connect to a `wss://` server URL and exchange JSON-RPC envelopes
            over the resulting socket. Subscribe methods return an integer
            subscription id; the server then pushes notification messages
            on the same socket. Unsubscribe with the matching unsubscribe
            method.

            Each method is documented as its own OpenAPI operation. The
            POST shape shown is illustrative — the request body is the
            JSON-RPC envelope you send over the WebSocket frame.
        """),
        version="1.0.0",
        servers=WEBSOCKET_SERVERS,
        tags=WEBSOCKET_TAGS,
        paths=websocket_paths,
    )

    with open(f"{out_dir}/websocket-rpc.yaml", "w") as f:
        f.write("# Generated by scripts/generate-rpc-specs.py — edit the generator, not this file.\n")
        yaml.dump(websocket_spec, f, sort_keys=False, allow_unicode=True, width=10000)

    print(f"Wrote websocket-rpc.yaml ({len(WEBSOCKET_METHODS)} methods)")



if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "api-specs"
    main(out)