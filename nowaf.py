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

# Default size is 8KB (8192 bytes)
DEFAULT_SIZE = 8 * 1024

# Prefix list for random JSON keys
PARAM_PREFIXES = [
    'id', 'user', 'session', 'token', 'auth', 'request', 'data', 'temp', 'cache',
    'author', 'authorID', 'authorName', 'authorized', 'autoupdate', 'avatar',
    'b', 'balance', 'ban', 'barcode', 'base', 'basket', 'batch', 'backup',
    'bill', 'binary', 'bio', 'birthdate', 'block', 'blog', 'board', 'body',
    'browser', 'btn', 'bucket', 'calendar', 'call', 'campaign', 'card', 'cart',
    'case', 'category', 'check', 'client', 'code', 'comment', 'config',
    'connection', 'content', 'cookie', 'country', 'course', 'create', 'data',
    'database', 'date', 'day', 'debug', 'delete', 'device', 'dir', 'download',
    'email', 'enable', 'entry', 'event', 'file', 'filter', 'form', 'folder',
    'friend', 'group', 'host', 'image', 'import', 'info', 'input', 'invoice'
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
    """Generate a random JSON key-value pair with junk data."""
    key = "token_" + generate_random_string(6)  # Changed to ensure token_ prefix
    value = generate_body(size, obfuscate)
    return {key: value}

def check_and_modify_json(request_text, size, obfuscate=False):
    """
    Check if the request contains JSON data and modify it by adding junk data.
    Returns the modified request.
    """
    try:
        # Split request into headers and body
        if "\r\n\r\n" in request_text:
            headers, body = request_text.split("\r\n\r\n", 1)
            separator = "\r\n\r\n"
        elif "\n\n" in request_text:
            headers, body = request_text.split("\n\n", 1)
            separator = "\n\n"
        else:
            # No body found, just headers
            body = ""
            headers = request_text
            separator = "\r\n\r\n"
        
        if body.strip():
            # Try to parse as JSON
            try:
                parsed_json = json.loads(body)
                
                # If it's a JSON object, add our junk data to it
                if isinstance(parsed_json, dict):
                    # Add status if not present
                    if "status" not in parsed_json:
                        parsed_json["status"] = "accepted"
                    
                    # Add the junk token data
                    junk_data = build_json_body(size, obfuscate)
                    parsed_json.update(junk_data)
                    
                    # Reconstruct the request
                    new_body = json.dumps(parsed_json)
                    return headers + separator + new_body
                else:
                    # Not a JSON object, use original method
                    junk_data = build_json_body(size, obfuscate)
                    # Try to merge if it's a list or other JSON type
                    if isinstance(parsed_json, list):
                        new_body = json.dumps([*parsed_json, junk_data])
                    else:
                        new_body = json.dumps({"original": parsed_json, **junk_data})
                    return headers + separator + new_body
                    
            except json.JSONDecodeError:
                # Body exists but is not JSON, append JSON after body
                junk_data = build_json_body(size, obfuscate)
                full_data = {"status": "accepted", **junk_data}
                new_body = body + "\n" + json.dumps(full_data)
                return headers + separator + new_body
        else:
            # No body found, create new JSON body
            junk_data = build_json_body(size, obfuscate)
            # Add status field
            full_data = {"status": "accepted", **junk_data}
            new_body = json.dumps(full_data)
            return headers + separator + new_body
            
    except Exception as e:
        # If anything goes wrong, fall back to original method
        junk_data = build_json_body(size, obfuscate)
        full_data = {"status": "accepted", **junk_data}
        return request_text + "\n\n" + json.dumps(full_data)

def add_body_to_request(request_text, size, obfuscate):
    """Legacy function for backward compatibility."""
    body = json.dumps(build_json_body(size, obfuscate))
    separator = "\r\n\r\n" if "\r\n\r\n" in request_text else "\n\n"
    return request_text + separator + body

def print_waf_list():
    print("Available WAF size presets:")
    print(f"Default: {DEFAULT_SIZE} bytes ({DEFAULT_SIZE/1024:.1f} KB)")
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
    parser = argparse.ArgumentParser(
        description=f"Generate large JSON bodies for testing servers. Default: {DEFAULT_SIZE} bytes ({DEFAULT_SIZE/1024:.1f} KB).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  %(prog)s payload.txt                  # Add {DEFAULT_SIZE} bytes of junk data
  %(prog)s 'GET / HTTP/1.1'             # Add {DEFAULT_SIZE} bytes to raw request
  %(prog)s payload.txt --size 16384     # Add 16KB of junk data
  %(prog)s payload.txt --waf aws        # Use AWS WAF preset (64KB)
  %(prog)s payload.txt --junk-multiplier 16  # Add 16KB (16 * 1024)
  %(prog)s payload.txt --obfuscate      # Use random characters instead of 'a's
  %(prog)s --list-wafs                  # List available WAF presets
        """
    )
    
    parser.add_argument("input", nargs="?", help="Payload text or file path")
    parser.add_argument("--size", type=int, help="Manual size in bytes")
    parser.add_argument("--waf", help="WAF preset for body size")
    parser.add_argument("--junk-multiplier", type=int, help="Generate (value * 1024) bytes")
    parser.add_argument("--list-wafs", action="store_true", help="List available WAF presets")
    parser.add_argument("--obfuscate", action="store_true", help="Use random characters instead of 'a'")
    parser.add_argument("--legacy", action="store_true", help="Use legacy mode (always append JSON)")
    parser.add_argument("--small", action="store_true", help=f"Use small size (1KB instead of default {DEFAULT_SIZE/1024}KB)")
    
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
    if args.small:
        size = 1024  # 1KB
    elif args.junk_multiplier:
        size = args.junk_multiplier * 1024
    elif args.size:
        size = args.size
    elif args.waf:
        size = WAF_SIZE_LIMITS.get(args.waf.lower(), DEFAULT_SIZE)
    else:
        size = DEFAULT_SIZE  # Default to 8KB

    # Load input payload
    if os.path.isfile(args.input):
        with open(args.input, "r") as f:
            request = f.read()
    else:
        request = args.input

    # Use the appropriate function
    if args.legacy:
        # Use original method
        result = add_body_to_request(request, size, args.obfuscate)
    else:
        # Use new method that checks for JSON and modifies it
        result = check_and_modify_json(request, size, args.obfuscate)
    
    print(result)

if __name__ == "__main__":
    main()