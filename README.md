# NOWAFPLZ
This tool is a conversion of infosec-au from [BurpSuite Extension](https://github.com/assetnote/nowafpls) to a stand alone tool.

It plays with the idea that WAFs will not monitor payloads if they are a certain size, this is to avoid high resource consumption, so what do we do? 
We send a large file so the WAF ignores it, this is a similar tactic used for AV on endpoints.

Many web application firewalls (WAFs) impose limits on how much of a request body they will inspect. For HTTP methods that include a body — such as POST, PUT, and PATCH — this can allow unintended behavior: if the request is padded with a sufficiently large amount of data, the WAF may only analyze the first portion and ignore anything beyond its inspection threshold.

Once the WAF reaches its processing limit, the remaining content in the request body is often passed directly to the origin server without inspection.

nowaf is a simple tool designed to help test this behavior. It appends a configurable amount of data to any raw HTTP request, allowing you to observe how a server or security appliance handles oversized bodies. You can choose from predefined size presets or specify a custom body size to match your testing needs.


# 📦 Installation

```
git clone https://github.com/yourname/nowaf.git
cd nowaf
python nowaf.py $payload
```

# 🧩 Flags Summary
- --size <bytes>	Custom body size
- --junk-multiplier <N>	Generates N × 1024 bytes
- --waf <name>	Use predefined size presets
- --list-wafs	Show all WAF preset options
- --obfuscate	Use random characters instead of "a"
- -h, --help	Show help message

# 🚀 Usage
Basic example

### Append a default 1024‑byte JSON body:
```
python nowaf.py request.txt
or
python nowwaf.py $payload.txt
```

### Use a WAF size preset
```
python nowaf.py request.txt --waf cloudflare
```

### List all presets
```
python nowaf.py --list-wafs
```
### Specify exact size
```
python nowaf.py request.txt --size 50000
```
### Use size multiplier (KB)
```
python nowaf.py request.txt --junk-multiplier 200
```

→ Generates 200 × 1024 = 204,800 bytes
Enable obfuscation mode
Use random characters instead of "a":
```
python nowaf.py request.txt --size 30000 --obfuscate
```

## 📄 Example Payload before:
It needs to be the full HTML request
```
GET /static/js/main.22728e1f.js HTTP/2
Host: lab-1767130908957-1api91.labs-app.bugforge.io
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Sec-Ch-Ua: "Chromium";v="141", "Not?A_Brand";v="8"
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36
Sec-Ch-Ua-Mobile: ?0
Accept: */*
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: no-cors
Sec-Fetch-Dest: script
Referer: https://lab-1767130908957-1api91.labs-app.bugforge.io/
Accept-Encoding: gzip, deflate, br
{"data":"Something important"}
```

## 📄 Example Payload after:
```
GET /static/js/main.22728e1f.js HTTP/2
Host: lab-1767130908957-1api91.labs-app.bugforge.io
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Sec-Ch-Ua: "Chromium";v="141", "Not?A_Brand";v="8"
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36
Sec-Ch-Ua-Mobile: ?0
Accept: */*
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: no-cors
Sec-Fetch-Dest: script
Referer: https://lab-1767130908957-1api91.labs-app.bugforge.io/
Accept-Encoding: gzip, deflate, br
{"data":"Something important"}
{"case_3fzSVc": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}

```

## 🛡 Disclaimer

This tool is intended for legal testing, research, and development on systems you own or have explicit permission to evaluate.

The author is not responsible for misuse of this software.
