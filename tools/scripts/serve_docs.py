"""資料の HTML 版（docs/_build/html/）を、同じネットワークのスマホやタブレットから見られるように
配信する。

- 全部のネットワークインタフェース（0.0.0.0）で待ち受け、スマホで開く URL と QR コードを表示する
- 研修のアプリが使う 8000 番と重ならないように、既定のポートは 8765
- WSL では mirrored モードでないとスマホから届かないので、そのときは直し方を表示する
- 先に `mise run docs`（または `mise run build`）で HTML 版を作っておく

使い方: python scripts/serve_docs.py [--port 8765]
"""

import argparse
import functools
import ipaddress
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from curriculum import DOCS

HTML = DOCS / "_build" / "html"
DEFAULT_PORT = 8765
# WSL が DNS のために lo に付けるアドレス。スマホからは使えない
WSL_DNS = ipaddress.IPv4Address("10.255.255.254")
TAILSCALE = ipaddress.IPv4Network("100.64.0.0/10")


def local_addresses() -> list[ipaddress.IPv4Address]:
    """スマホから届く可能性のある IPv4 アドレス。LAN のアドレスを先に並べる。"""
    out = subprocess.run(["hostname", "-I"], capture_output=True, text=True).stdout.split()
    addrs = []
    for word in out:
        try:
            addr = ipaddress.ip_address(word)
        except ValueError:
            continue
        if isinstance(addr, ipaddress.IPv4Address) and not addr.is_loopback and addr != WSL_DNS:
            addrs.append(addr)
    return sorted(addrs, key=lambda a: (a in TAILSCALE, not a.is_private, a))


def label(addr: ipaddress.IPv4Address) -> str:
    if addr in TAILSCALE:
        return "Tailscale（スマホにも Tailscale が要る）"
    return "同じ Wi-Fi・LAN" if addr.is_private else "グローバル"


def magic_dns_name(addr: ipaddress.IPv4Address) -> str | None:
    """Tailscale の MagicDNS の名前（*.ts.net）。引けなければ None。"""
    import socket

    try:
        name = socket.gethostbyaddr(str(addr))[0]
    except OSError:
        return None
    return name if name.endswith(".ts.net") else None


def wsl_mode() -> str | None:
    """WSL のネットワークのモード（mirrored・nat）。WSL でなければ None。"""
    if "microsoft" not in Path("/proc/version").read_text().lower():
        return None
    try:
        out = subprocess.run(["wslinfo", "--networking-mode"], capture_output=True, text=True)
    except FileNotFoundError:
        return "unknown"
    return out.stdout.strip() or "unknown"


def print_qr(url: str) -> None:
    import segno

    segno.make(url, error="m").terminal(compact=True)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="資料の HTML 版をスマホから見られるように配信する")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args(argv)
    if not (HTML / "index.html").exists():
        print("HTML 版がありません。先に `mise run docs -- --no-pdf` を実行してください")
        return 1

    addrs = local_addresses()
    print(f"資料の HTML 版を配信します（{HTML}）。止めるときは Ctrl+C\n")
    print(f"  この PC:  http://127.0.0.1:{args.port}/")
    for addr in addrs:
        print(f"  {label(addr)}:  http://{addr}:{args.port}/")
        if addr in TAILSCALE and (name := magic_dns_name(addr)):
            print(f"  Tailscale（名前）:  http://{name}:{args.port}/")
    if addrs:
        print("\nスマホのカメラで読み取る（同じ Wi-Fi につないでおく）:")
        print_qr(f"http://{addrs[0]}:{args.port}/")

    mode = wsl_mode()
    if mode is not None and mode != "mirrored":
        print(
            f"\n注意: WSL のネットワークが {mode} モードなので、スマホからは届きません。"
            "\n  Windows の %UserProfile%\\.wslconfig に次の2行を書き、"
            "PowerShell で `wsl --shutdown` してから開き直してください:"
            "\n    [wsl2]\n    networkingMode=mirrored"
        )
    if mode is not None:
        print(
            "\nスマホから開けないときは、Windows のファイアウォールで受信を許可します"
            "（管理者の PowerShell で1回だけ）:"
            "\n  New-NetFirewallHyperVRule -Name handsoff-docs -DisplayName 'handsoff docs'"
            " -Direction Inbound -VMCreatorId '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}'"
            f" -Protocol TCP -LocalPorts {args.port}"
        )

    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(HTML))
    with ThreadingHTTPServer(("0.0.0.0", args.port), handler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n止めました")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
