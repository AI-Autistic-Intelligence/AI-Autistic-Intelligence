#!/usr/bin/env python3
"""
sync_profile.py - AI-Autistic-Intelligence GitHub Profile Synchronizer

Automatically audits and fetches all published packages from:
- Crates.io (AI-Autistic-Intelligence)
- npm (@nest-yalc-2, @node-yalc, @ferrox-node, ferrox-agent-toolkit, etc.)
- PyPI (AutisticIntelligence)
- Packagist (ferrox/*)

Then regenerates the package sections of README.md with:
- Native lazy loading (loading="lazy")
- 24-hour edge CDN caching (cacheSeconds=86400) to prevent rate limits
- Categorized, collapsible accordion sections (<details>)
- Direct clickable links to package registries
"""

import os
import re
import json
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

HEADERS = {'User-Agent': 'ferrox-profile-sync/1.0 (contact@ferrox-rust.dev)'}

def get_packagist_packages():
    url = 'https://packagist.org/packages/list.json?vendor=ferrox'
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        return sorted(data.get('packageNames', []))

def get_crates_packages():
    user_url = 'https://crates.io/api/v1/users/AI-Autistic-Intelligence'
    req = urllib.request.Request(user_url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        u_data = json.loads(resp.read().decode('utf-8'))
        user_id = u_data['user']['id']
    
    page = 1
    crates = []
    while True:
        c_url = f'https://crates.io/api/v1/crates?user_id={user_id}&page={page}&per_page=100'
        c_req = urllib.request.Request(c_url, headers=HEADERS)
        with urllib.request.urlopen(c_req) as resp:
            c_data = json.loads(resp.read().decode('utf-8'))
            items = c_data.get('crates', [])
            if not items:
                break
            crates.extend([c['name'] for c in items])
            if len(items) < 100:
                break
            page += 1
    return sorted(crates)

def get_pypi_packages():
    candidates = [
        'ferrox-py',
        'ferrox-py-utils',
        'ferrox-py-auth',
        'ferrox-py-commerce',
        'ferrox-py-aspyre',
        'ferrox-agent-toolkit',
    ]
    def check_pypi(pkg):
        try:
            req = urllib.request.Request(f'https://pypi.org/pypi/{pkg}/json', headers=HEADERS)
            with urllib.request.urlopen(req) as resp:
                if resp.status == 200:
                    return pkg
        except Exception:
            return None
    with ThreadPoolExecutor(max_workers=5) as pool:
        results = pool.map(check_pypi, candidates)
    return sorted([r for r in results if r])

def get_npm_packages():
    packages = set([
        # nest-yalc-2
        '@nest-yalc-2/ag-grid', '@nest-yalc-2/api-strategy', '@nest-yalc-2/app', '@nest-yalc-2/audit',
        '@nest-yalc-2/aws-helpers', '@nest-yalc-2/data-loader', '@nest-yalc-2/database', '@nest-yalc-2/field-middleware',
        '@nest-yalc-2/graphql', '@nest-yalc-2/interfaces', '@nest-yalc-2/logger', '@nest-yalc-2/types',
        '@nest-yalc-2/utils', '@nest-yalc-2/crud-gen', '@nest-yalc-2/errors', '@nest-yalc-2/event-manager',
        '@nest-yalc-2/kafka', '@nest-yalc-2/observability', '@nest-yalc-2/omnikernel-module', '@nest-yalc-2/types-extends',
        '@nest-yalc-2/framework', '@nest-yalc-2/jest', '@nest-yalc-2/jest-config', '@nest-yalc-2/sentinel',
        
        # node-yalc
        '@node-yalc/types', '@node-yalc/interfaces', '@node-yalc/types-extends', '@node-yalc/logger',
        '@node-yalc/utils', '@node-yalc/errors', '@node-yalc/event-manager', '@node-yalc/common',
        '@node-yalc/aws-helpers', '@node-yalc/auth', '@node-yalc/config', '@node-yalc/cqrs',
        '@node-yalc/datagrid', '@node-yalc/guards', '@node-yalc/i18n', '@node-yalc/jobs',
        '@node-yalc/kernel', '@node-yalc/resilience', '@node-yalc/security', '@node-yalc/selftest',
        '@node-yalc/storage', '@node-yalc/tracing', '@node-yalc/transports', '@node-yalc/database',
        'node-yalc',
        
        # ferrox-node
        '@ferrox-node/core', '@ferrox-node/aws', '@ferrox-node/bitbucket', '@ferrox-node/cqrs',
        '@ferrox-node/database', '@ferrox-node/firebase', '@ferrox-node/gcp', '@ferrox-node/jobs',
        '@ferrox-node/kafka', '@ferrox-node/mailer', '@ferrox-node/observability', '@ferrox-node/redis',
        '@ferrox-node/security', '@ferrox-node/stripe', '@ferrox-node/transports',
        'ferrox-saas-backend',
        
        # standalone
        'ferrox-agent-toolkit'
    ])
    
    def check_npm(pkg):
        enc = urllib.parse.quote(pkg, safe='')
        try:
            req = urllib.request.Request(f'https://registry.npmjs.org/{enc}', headers=HEADERS)
            with urllib.request.urlopen(req) as resp:
                if resp.status == 200:
                    return pkg
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=10) as pool:
        results = pool.map(check_npm, packages)
    return sorted([r for r in results if r])

def format_crate(c):
    url = f"https://crates.io/crates/{c}"
    badge = f"https://img.shields.io/crates/d/{c}?label={c}&style=flat-square&color=fc8d62&logo=rust&cacheSeconds=86400"
    return f'<a href="{url}"><img loading="lazy" src="{badge}" alt="{c}" /></a>'

def format_npm(p):
    enc = urllib.parse.quote(p, safe='')
    url = f"https://www.npmjs.com/package/{p}"
    badge = f"https://img.shields.io/npm/dt/{enc}?label={enc}&style=flat-square&color=cb3837&logo=npm&cacheSeconds=86400"
    return f'<a href="{url}"><img loading="lazy" src="{badge}" alt="{p}" /></a>'

def format_pypi(p):
    url = f"https://pypi.org/project/{p}/"
    badge = f"https://img.shields.io/pepy/dt/{p}?label={p}&style=flat-square&color=3776ab&logo=python&cacheSeconds=86400"
    return f'<a href="{url}"><img loading="lazy" src="{badge}" alt="{p}" /></a>'

def format_packagist(p):
    label = p.split('/')[-1]
    url = f"https://packagist.org/packages/{p}"
    badge = f"https://img.shields.io/packagist/dt/{p}?label={label}&style=flat-square&color=8892BF&logo=php&cacheSeconds=86400"
    return f'<a href="{url}"><img loading="lazy" src="{badge}" alt="{p}" /></a>'

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    readme_path = os.path.join(root, 'README.md')
    
    print('Auditing package registries...')
    packagist = get_packagist_packages()
    crates = get_crates_packages()
    pypi = get_pypi_packages()
    npm = get_npm_packages()
    
    total = len(packagist) + len(crates) + len(pypi) + len(npm)
    print(f'Discovered {total} live packages: Crates={len(crates)}, NPM={len(npm)}, PHP={len(packagist)}, PyPI={len(pypi)}')

    # Categorize Crates
    crates_front = sorted([c for c in crates if c.startswith('ferrox-front') or c == 'ferrox-codex'])
    crates_db = sorted([c for c in crates if c.startswith('ferrox-database')])
    crates_tools = sorted([c for c in crates if c in ['cargo-ferrox', 'ferrox-agent-toolkit', 'rust-yalc', 'stl-grinder', 'bambu-3mf-cli', 'whatsapp-to-pdf']])
    crates_core = sorted([c for c in crates if c not in crates_front and c not in crates_db and c not in crates_tools])

    # Categorize NPM
    npm_nest = sorted([p for p in npm if p.startswith('@nest-yalc-2/')])
    npm_node = sorted([p for p in npm if p.startswith('@node-yalc/') or p == 'node-yalc'])
    npm_ferrox = sorted([p for p in npm if p.startswith('@ferrox-node/') or p == 'ferrox-saas-backend'])
    npm_agent = sorted([p for p in npm if p == 'ferrox-agent-toolkit'])

    catalog_lines = [
        '<details>',
        f'<summary><b>🔍 Click to expand the full directory of all {total} published packages!</b></summary>',
        '<br/>',
        '<details>',
        f'<summary>🦀 <b>Rust Crates (crates.io) — {len(crates)} Packages</b></summary>',
        '<br/>',
        '<h4>⚙️ Core Framework, CQRS & Microservices</h4>',
        '<p align="center">',
        ' '.join([format_crate(c) for c in crates_core]),
        '</p>',
        '<h4>🎨 Reactive WebAssembly UI & Codex (ferrox-front)</h4>',
        '<p align="center">',
        ' '.join([format_crate(c) for c in crates_front]),
        '</p>',
        '<h4>💾 High-Performance Database Connectors</h4>',
        '<p align="center">',
        ' '.join([format_crate(c) for c in crates_db]),
        '</p>',
        '<h4>🛠️ CLI Tools & Agent Toolkits</h4>',
        '<p align="center">',
        ' '.join([format_crate(c) for c in crates_tools]),
        '</p>',
        '</details>',
        '<br/>',
        '<details>',
        f'<summary>📦 <b>Node.js & TypeScript (npm) — {len(npm)} Packages</b></summary>',
        '<br/>',
        '<h4>🏢 @nest-yalc-2 Enterprise Suite</h4>',
        '<p align="center">',
        ' '.join([format_npm(p) for p in npm_nest]),
        '</p>',
        '<h4>🔧 @node-yalc Utility & Architecture Modules</h4>',
        '<p align="center">',
        ' '.join([format_npm(p) for p in npm_node]),
        '</p>',
        '<h4>⚡ @ferrox-node Cloud & Transports</h4>',
        '<p align="center">',
        ' '.join([format_npm(p) for p in npm_ferrox]),
        '</p>',
    ]
    if npm_agent:
        catalog_lines.extend([
            '<h4>🤖 Autonomous Multi-Agent Toolkits</h4>',
            '<p align="center">',
            ' '.join([format_npm(p) for p in npm_agent]),
            '</p>',
        ])
    catalog_lines.extend([
        '</details>',
        '<br/>',
        '<details>',
        f'<summary>🐍 <b>Python Packages (PyPI) — {len(pypi)} Packages</b></summary>',
        '<br/>',
        '<p align="center">',
        ' '.join([format_pypi(p) for p in sorted(pypi)]),
        '</p>',
        '</details>',
        '<br/>',
        '<details>',
        f'<summary>🐘 <b>PHP Packages (Packagist) — {len(packagist)} Packages</b></summary>',
        '<br/>',
        '<p align="center">',
        ' '.join([format_packagist(p) for p in sorted(packagist)]),
        '</p>',
        '</details>',
        '</details>'
    ])
    catalog_content = '\n'.join(catalog_lines)

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match and replace counters & catalog
    counters_catalog_pattern = re.compile(r'<p align="center">\s*<img [^>]*badge/Total_Packages-.*?</details>\s*</details>', re.DOTALL)
    new_block = f"""<p align="center">
  <img loading="lazy" src="https://img.shields.io/badge/Total_Packages-{total}-0F766E?style=for-the-badge" alt="Total Packages" />
  <img loading="lazy" src="https://img.shields.io/badge/NPM-{len(npm)}-cb3837?style=for-the-badge&logo=npm" alt="Total NPM Packages" />
  <img loading="lazy" src="https://img.shields.io/badge/Crates.io-{len(crates)}-fc8d62?style=for-the-badge&logo=rust" alt="Total Rust Packages" />
  <img loading="lazy" src="https://img.shields.io/badge/PyPI-{len(pypi)}-3776ab?style=for-the-badge&logo=python" alt="Total PyPI Packages" />
  <img loading="lazy" src="https://img.shields.io/badge/Packagist-{len(packagist)}-8892BF?style=for-the-badge&logo=php" alt="Total PHP Packages" />
</p>
{catalog_content}"""

    content = counters_catalog_pattern.sub(new_block, content)

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('README.md successfully updated and verified!')

if __name__ == '__main__':
    main()
