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


def build_operation(method, base_note=ENDPOINT_NOTE, historical=False):
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


def build_paths(methods, base_path_prefix="", base_note=ENDPOINT_NOTE, historical=False):
    paths = _OD()
    for m in methods:
        path = f"{base_path_prefix}/{m['name']}"
        paths[path] = _OD([("post", build_operation(m, base_note=base_note, historical=historical))])
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
    description="Returns information associated with the account at the given pubkey, including its lamport balance, owner program, executable flag, rent epoch, and data.",
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
    description="Returns the lamport balance of the account at the provided pubkey.",
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
    description="Returns account information for a list of pubkeys (max 100 per request).",
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
    description="Returns all accounts owned by the provided program pubkey. Heavy query — prefer paginated alternatives where possible.",
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
    description="Returns the token balance of an SPL token account.",
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
    description="Returns all SPL token accounts whose delegate matches the provided pubkey.",
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
    description="Returns all SPL token accounts owned by the provided pubkey, optionally filtered by mint or token program.",
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
    description="Returns the 20 largest token accounts for a given mint, sorted descending by balance.",
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
    description="Returns the total circulating supply of an SPL token mint.",
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
    description="Returns identity and transaction information about a confirmed block in the ledger.",
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
    description="Returns the current block height of the node.",
    params=[config_param()],
    params_example=[{"commitment": "finalized"}],
    result_schema=s_int(desc="Current block height.", example=395090168),
    result_example=395090168,
)

add_solana(
    name="getBlocks", tag="Block",
    summary="Confirmed blocks in a range",
    description="Returns a list of confirmed blocks between two slots (inclusive).",
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
    description="Returns up to `limit` confirmed blocks starting at `startSlot`.",
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
    description="Returns the estimated Unix timestamp at which a block was produced.",
    params=[{"name": "slot", "schema_doc": "Slot number.", "schema": s_int(example=416997240), "required": True}],
    params_example=[378967388],
    result_schema=s_int(nullable=True, desc="Unix timestamp seconds, or null if unavailable."),
    result_example=1777683570,
)

add_solana(
    name="getBlockCommitment", tag="Block",
    summary="Commitment for a block",
    description="Returns the amount of cluster stake in lamports that has voted on a particular block.",
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
    description="Returns recent block production information from the current or previous epoch.",
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
    description="Returns information about all the nodes participating in the cluster.",
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
    description="Returns information about the current epoch, including absolute slot, slot index, and slots in the epoch.",
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
    description="Returns the genesis hash of the cluster.",
    params=[],
    params_example=[],
    result_schema=s_string(desc="Base-58 genesis hash."),
    result_example="5eykt4UsFv8P8NJdTREpY1vzqKqZKvdpKuc147dw2N9d",
)

add_solana(
    name="getHealth", tag="Cluster",
    summary="Node health",
    description="Returns `ok` if the node is healthy, otherwise an error.",
    params=[],
    params_example=[],
    result_schema=s_string(enum=["ok"], desc="Node health status."),
    result_example="ok",
)

add_solana(
    name="getIdentity", tag="Cluster",
    summary="Node identity",
    description="Returns the identity pubkey of the current node.",
    params=[],
    params_example=[],
    result_schema=s_obj(properties=[("identity", s_string())]),
    result_example={"identity": "9bupGu2BbLbPCb1ZUAswM3GBVfnKsYWBJjJixD5N5cYm"},
)

add_solana(
    name="getVersion", tag="Cluster",
    summary="Solana version",
    description="Returns the Solana software version running on the node.",
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
    description="Returns the estimated fee in lamports for a base-64 encoded compiled message.",
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
    description="Returns the latest blockhash and the last block height at which it will be valid.",
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
    description="Returns whether a blockhash is still valid.",
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
    description="Returns the minimum balance (in lamports) required for an account of the given size to be rent-exempt.",
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
    description="Returns recent priority fees observed in the last 150 blocks, optionally constrained to accounts.",
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
    description="Returns confirmed signatures for transactions involving the given address, newest first.",
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
    description="Returns the statuses of a list of transaction signatures.",
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
    description="Returns transaction details for a confirmed signature.",
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
    description="Returns the cumulative count of transactions processed since the cluster started.",
    params=[config_param()],
    params_example=[{"commitment": "finalized"}],
    result_schema=s_int(),
    result_example=509155823874,
)

add_solana(
    name="sendTransaction", tag="Transactions",
    summary="Submit a signed transaction",
    description="Submits a fully-signed, encoded transaction to the cluster for processing.",
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
    description="Simulates a transaction without committing it. Useful for verifying account changes and estimating compute.",
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
    description="Returns the slot that has reached the given commitment level.",
    params=[config_param()],
    params_example=[{"commitment": "finalized"}],
    result_schema=s_int(example=416997240),
    result_example=416997240,
)

add_solana(
    name="getSlotLeader", tag="Slots",
    summary="Current slot leader",
    description="Returns the current slot leader pubkey.",
    params=[config_param()],
    params_example=[{"commitment": "finalized"}],
    result_schema=s_string(),
    result_example="DRpbCBMxVnDK7maPM5tGv6MvB3v1sRMC86PZ8okm21hy",
)

add_solana(
    name="getSlotLeaders", tag="Slots",
    summary="Slot leaders for a range",
    description="Returns the slot leaders for a contiguous range of slots.",
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
    description="Returns the leader schedule for an epoch.",
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
    description="Returns the minimum delegation, in lamports, for a stake account.",
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
    description="Returns information about all vote accounts in the current and delinquent buckets.",
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
    description="Returns the current inflation governor (initial, terminal, taper, foundation, foundationTerm).",
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
    description="Returns the specific inflation values for the current epoch.",
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
    description="Returns the inflation rewards for a list of addresses for an epoch.",
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
    description="Returns information about the total supply of SOL.",
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
    description="Returns the 20 largest accounts by lamport balance, optionally filtered by circulating / non-circulating.",
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
    description="Requests an airdrop of lamports to the given pubkey. Available on devnet/testnet only.",
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
    description="Returns the lowest slot the node has information about in its ledger.",
    params=[],
    params_example=[],
    result_schema=s_int(),
    result_example=349200000,
)

add_solana(
    name="getRecentPerformanceSamples", tag="Misc",
    summary="Recent performance samples",
    description="Returns up to `limit` recent performance samples in reverse slot order.",
    params=[{"name": "limit", "schema_doc": "Number of samples to return (1–720).", "schema": s_int(example=5), "required": False}],
    params_example=[5],
    result_schema=s_arr(s_obj(properties=[
        ("slot", s_int()), ("numTransactions", s_int()), ("numSlots", s_int()),
        ("samplePeriodSecs", s_int()), ("numNonVoteTransactions", s_int()),
    ])),
    result_example=[{"slot": 416997380, "numTransactions": 168226, "numSlots": 152, "samplePeriodSecs": 60, "numNonVoteTransactions": 54837}, {"slot": 416997228, "numTransactions": 174204, "numSlots": 158, "samplePeriodSecs": 60, "numNonVoteTransactions": 56218}, {"slot": 416997070, "numTransactions": 167063, "numSlots": 145, "samplePeriodSecs": 60, "numNonVoteTransactions": 58812}],
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
    description="Returns identity and transaction information about a historical block by slot, served from SVS's long-term ledger storage.",
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
    description="Returns confirmed blocks between two historical slots (inclusive).",
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
    description="Returns up to `limit` confirmed historical blocks starting at `startSlot`.",
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
    description="Returns the estimated Unix timestamp at which a historical block was produced.",
    params=[{"name": "slot", "schema_doc": "Slot number.", "schema": s_int(example=178000000), "required": True}],
    params_example=[178000000],
    result_schema=s_int(nullable=True),
    result_example=1700000000,
)

add_historical(
    name="getFirstAvailableBlock", tag="Block",
    summary="Lowest historical block",
    description="Returns the lowest slot number that the historical archive has data for.",
    params=[],
    params_example=[],
    result_schema=s_int(),
    result_example=140000000,
)

add_historical(
    name="getSlot", tag="Slots",
    summary="Highest historical slot",
    description="Returns the highest slot number that the historical archive has data for.",
    params=[config_param()],
    params_example=[{"commitment": "finalized"}],
    result_schema=s_int(),
    result_example=416990000,
)

add_historical(
    name="getSignaturesForAddress", tag="Transactions",
    summary="Historical signatures for an address",
    description="Returns historical signatures involving an address from SVS's long-term ledger storage.",
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
    description="Returns confirmation status for historical signatures.",
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
    description="Returns full transaction data for a historical signature.",
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
    {"url": "https://public.rpc.solanavibestation.com",  "description": "Public endpoint, /historical path (rate-limited)"},
    {"url": "https://basic.rpc.solanavibestation.com",   "description": "Basic tier, /historical path"},
    {"url": "https://ultra.rpc.solanavibestation.com",   "description": "Ultra tier, /historical path"},
    {"url": "https://elite.rpc.solanavibestation.com",   "description": "Elite tier, /historical path"},
    {"url": "https://epic.rpc.solanavibestation.com",    "description": "Epic tier, /historical path"},
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
    historical_paths = build_paths(HISTORICAL_METHODS, base_path_prefix="/historical", base_note=HISTORICAL_ENDPOINT_NOTE, historical=True)

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
            Historical Solana JSON-RPC 2.0 endpoints hosted by Solana Vibe Station,
            served from long-term ledger storage.

            All requests POST to **`/historical`** on the chosen server URL. The
            per-method paths shown here (e.g. `/historical/getBlock`) are
            documentation groupings so each operation renders separately.
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


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "api-specs"
    main(out)
