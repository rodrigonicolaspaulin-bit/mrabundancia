#!/usr/bin/env python3
"""Respaldo y alta de etiquetas/campos de ManyChat para el SOP v8 de Mr. Abundancia.

Uso (desde una maquina con acceso a api.manychat.com):

    export MANYCHAT_API_KEY="..."   # Settings -> API de la cuenta de Instagram de Mr. Abundancia
    python3 scripts/manychat_api.py info               # confirma que la clave es de la cuenta correcta
    python3 scripts/manychat_api.py backup             # respaldo de solo lectura en backups/<fecha>/
    python3 scripts/manychat_api.py setup              # simulacion: muestra que se crearia
    python3 scripts/manychat_api.py setup --apply      # crea lo que falta (nunca borra ni renombra)

La API publica de ManyChat no permite crear ni editar flujos: los flujos se arman en el
editor siguiendo manychat/ESPECIFICACION_FLUJOS_v8.md. Este script solo cubre respaldo,
etiquetas, campos personalizados y campos del bot.
"""
import argparse
import datetime
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

API = "https://api.manychat.com"
ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / "manychat" / "config_v8.json"

READ_ENDPOINTS = {
    "info": "/fb/page/getInfo",
    "tags": "/fb/page/getTags",
    "custom_fields": "/fb/page/getCustomFields",
    "bot_fields": "/fb/page/getBotFields",
    "flows": "/fb/page/getFlows",
    "growth_tools": "/fb/page/getGrowthTools",
}


def call(path, payload=None):
    key = os.environ.get("MANYCHAT_API_KEY")
    if not key:
        sys.exit("Falta MANYCHAT_API_KEY")
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        API + path,
        data=data,
        method="POST" if payload is not None else "GET",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"{path}: HTTP {e.code} {e.read().decode(errors='replace')}")
    if body.get("status") != "success":
        sys.exit(f"{path}: {body}")
    return body.get("data")


def cmd_info(_):
    print(json.dumps(call(READ_ENDPOINTS["info"]), indent=2, ensure_ascii=False))


def cmd_backup(_):
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = ROOT / "backups" / stamp
    out.mkdir(parents=True, exist_ok=True)
    for name, path in READ_ENDPOINTS.items():
        (out / f"{name}.json").write_text(json.dumps(call(path), indent=2, ensure_ascii=False))
        print(f"ok {name}")
    print(f"Respaldo en {out}")


def cmd_setup(args):
    cfg = json.loads(CONFIG.read_text())
    tags = {t["name"] for t in call(READ_ENDPOINTS["tags"])}
    fields = {f["name"] for f in call(READ_ENDPOINTS["custom_fields"])}
    bot_fields = {f["name"] for f in call(READ_ENDPOINTS["bot_fields"])}

    todo = []
    todo += [("/fb/page/createTag", {"name": t}) for t in cfg["tags"] if t not in tags]
    todo += [
        ("/fb/page/createCustomField", {k: f[k] for k in ("caption", "type", "description")})
        for f in cfg["custom_fields"] if f["caption"] not in fields
    ]
    for f in cfg["bot_fields"]:
        if f["name"] in bot_fields:
            continue
        payload = {"name": f["name"], "type": f["type"], "description": f["description"]}
        if f["value"] is not None:
            payload["value"] = f["value"]
        todo.append(("/fb/page/createBotField", payload))

    for t in cfg["legacy_tags_keep"]:
        print(f"conservar (no se toca): {t} {'(existe)' if t in tags else '(no existe)'}")
    if not todo:
        print("Nada que crear.")
        return
    for path, payload in todo:
        if args.apply:
            call(path, payload)
            print(f"creado  {path} {payload}")
        else:
            print(f"crearia {path} {payload}")
    if not args.apply:
        print("Simulacion. Repetir con --apply para crear.")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("info").set_defaults(fn=cmd_info)
    sub.add_parser("backup").set_defaults(fn=cmd_backup)
    s = sub.add_parser("setup")
    s.add_argument("--apply", action="store_true")
    s.set_defaults(fn=cmd_setup)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
