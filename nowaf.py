#!/usr/bin/env python3
import sys
import random
import string
import os
import json
import argparse

# Default charset for obfuscation
OBFUSCATION_CHARSET = string.ascii_letters + string.digits + "-_"

# WAF size presets (approx bytes)
WAF_SIZE_LIMITS = {
    "cloudflare": 128 * 1024,
    "aws": 64 * 1024,
    "akamai": 128 * 1024,
    "azure": 128 * 1024,
    "fortiweb": 100 * 1024 * 1024,
    "barracuda": 64 * 1024,
    "sucuri": 10 * 1024 * 1024,
    "radware": 1 * 1024 * 1024 * 1024,
    "f5": 20 * 1024 * 1024,
    "paloalto": 10 * 1024 * 1024,
    "cloudarmor": 128 * 1024
}

# Prefix list for random JSON keys
PARAM_PREFIXES = [
    'id', 'user', 'session', 'token', 'auth', 'request', 'data', 'temp', 'cache',
    'author', 'authorID', 'authorName', 'authorized', 'autoupdate', 'avatar', 'b',
    'balance', 'ban', 'barcode', 'base', 'basket', 'batch', 'backup', 'bill', 'binary',
    'bio', 'birthdate', 'block', 'blog', 'board', 'body', 'browser', 'btn', 'bucket',
    'calendar', 'call', 'campaign', 'card', 'cart', 'case', 'category', 'check',
    'client', 'code', 'comment', 'config', 'connection', 'content', 'cookie', 'country',
    'course', 'create', 'data', 'database', 'date', 'day', 'debug', 'delete', 'device',
    'dir', 'download', 'email', 'enable', 'entry', 'event', 'file', 'filter', 'form',
    'folder', 'friend', 'group', 'host', 'image', 'import', 'info', 'input', 'invoice'
]

def generate_random_string(length, charset=OBFUSCATION_CHARSET):
    return ''.join(random.choice(charset) for _ in range(length))

def generate_random_param():
    prefix = random.choice(PARAM_PREFIXES)
    suffix = generate_random_string(6)
    return f"{prefix}_{suffix}"

def generate_body(size, obfuscate=False):
    """Generate filler content: 'a' * size OR random characters."""
    if obfuscate:
        return generate_random_string(size)
    return "a" * size

def build_json_body(size, obfuscate=False):
    key = generate_random_param()
    value = generate_body(size, obfuscate)
    return json.dumps({key: value})

def add_body_to_request(request_text, size, obfuscate):
    body = build_json_body(size, obfuscate)

    separator = "\r\n\r\n" if "\r\n\r\n" in request_text else "\n\n"
    return request_text + separator + body

def print_waf_list():
    print("Available WAF size presets:")
    print("cloudflare\t128 KB for ruleset engine, up to 500 MB for enterprise")
    print("aws\t8 KB - 64 KB (configurable depending on service)")
    print("akamai\t8 KB - 128 KB")
    print("azure\t128 KB")
    print("fortiweb\t100 MB")
    print("barracuda\t64 KB")
    print("sucuri\t10 MB")
    print("radware\tup to 1 GB for cloud WAF")
    print("f5\t20 MB (configurable)")
    print("paloalto\t10 MB")
    print("cloudarmor\t8 KB (can be increased to 128 KB)")

def main():
    parser = argparse.ArgumentParser(description="Generate large JSON bodies for testing servers.")
    parser.add_argument("input", nargs="?", help="Payload text or file path")

    parser.add_argument("--size", type=int, help="Manual size in bytes")
    parser.add_argument("--waf", help="WAF preset for body size")
    parser.add_argument("--junk-multiplier", type=int, help="Generate (value * 1024) bytes")
    parser.add_argument("--list-wafs", action="store_true", help="List available WAF presets")
    parser.add_argument("--obfuscate", action="store_true", help="Use random characters instead of 'a'")

    args = parser.parse_args()

    # Handle WAF list request
    if args.list_wafs:
        print_waf_list()
        return

    # Require input unless listing WAFs
    if not args.input:
        parser.print_help()
        return

    # Determine size priority
    if args.junk_multiplier:
        size = args.junk_multiplier * 1024
    elif args.size:
        size = args.size
    elif args.waf:
        size = WAF_SIZE_LIMITS.get(args.waf.lower(), 1024)
    else:
        size = 1024

    # Load input payload
    if os.path.isfile(args.input):
        with open(args.input, "r") as f:
            request = f.read()
    else:
        request = args.input

    result = add_body_to_request(request, size, args.obfuscate)
    print(result)

if __name__ == "__main__":
    main()
