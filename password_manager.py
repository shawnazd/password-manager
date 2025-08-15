import json
import os
import sys
import hashlib
from getpass import getpass
from datetime import datetime

# -----------------------------------
# Paths (created next to this script)
# -----------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
DB_PATH = os.path.join(BASE_DIR, "passwords.json")


# --------------- Utils ---------------
def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

def fmt_updated(iso_str: str) -> str:
    try:
        return datetime.fromisoformat(iso_str).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso_str or ""

def read_json(path, default):
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def print_table(rows, headers):
    """Pretty table with dynamic column width and clean alignment."""
    if not rows:
        print("No data to display.")
        return

    norm = [list(r)[:len(headers)] + [""] * max(0, len(headers) - len(r)) for r in rows]

    widths = [len(h) for h in headers]
    for r in norm:
        for i, v in enumerate(r):
            widths[i] = max(widths[i], len(str(v)))

    header_line = " | ".join(f"{headers[i]:<{widths[i]}}" for i in range(len(headers)))
    sep = "-" * (sum(widths) + 3 * (len(headers) - 1))
    print(header_line)
    print(sep)
    for r in norm:
        print(" | ".join(f"{str(r[i]):<{widths[i]}}" for i in range(len(headers))))

def pause():
    input("\nPress Enter to continue...")


# -------- Registration / Login --------
def ensure_registered():
    cfg = read_json(CONFIG_PATH, {})
    if cfg.get("master_hash"):
        return
    print("=== First-time setup: Create Master Password ===")
    while True:
        pw1 = getpass("Create master password: ").strip()
        pw2 = getpass("Confirm master password: ").strip()
        if not pw1:
            print("Master password cannot be empty.\n")
            continue
        if pw1 != pw2:
            print("Passwords do not match. Try again.\n")
            continue
        break
    cfg = {"master_hash": sha256(pw1), "created_at": now_iso()}
    write_json(CONFIG_PATH, cfg)
    print("✅ Master password set.\n")

def login():
    cfg = read_json(CONFIG_PATH, {})
    if not cfg.get("master_hash"):
        print("No master password found. Run setup again.")
        sys.exit(1)
    print("=== Login ===")
    for _ in range(3):
        pw = getpass("Enter master password: ").strip()
        if sha256(pw) == cfg["master_hash"]:
            print("✅ Login successful.\n")
            return
        print("❌ Incorrect password.")
    print("Too many failed attempts. Exiting.")
    sys.exit(1)


# --------- DB load/save helpers ---------
def load_db():
    db = read_json(DB_PATH, {})
    if not db or "items" not in db or "next_id" not in db:
        db = {"next_id": 1, "items": []}
        write_json(DB_PATH, db)
    return db

def save_db(db):
    write_json(DB_PATH, db)

def next_id(db):
    nid = int(db.get("next_id", 1))
    db["next_id"] = nid + 1
    return nid

def find_by_id(db, eid: int):
    for it in db.get("items", []):
        if it.get("id") == eid:
            return it
    return None


# --------------- CRUD ----------------
def add_entry(db):
    print("=== Add New Entry ===")
    name = input("Name (e.g., Gmail, Facebook): ").strip()
    username = input("Username: ").strip()
    password = getpass("Password: ").strip()
    auth_key = input("Authentication key (optional): ").strip()
    website = input("Website URL: ").strip()
    notes = input("Notes: ").strip()

    item = {
        "id": next_id(db),
        "name": name,
        "username": username,
        "password": password,
        "auth_key": auth_key,
        "website": website,
        "notes": notes,
        "updated_at": now_iso(),
    }
    db["items"].append(item)
    save_db(db)
    print(f"✅ Added entry with ID {item['id']}.")

def list_entries(db):
    items = sorted(db.get("items", []), key=lambda x: x.get("id", 0))
    if not items:
        print("No entries found.")
        return
    headers = ["ID", "Name", "Username", "Password", "Auth Key", "Website", "Notes", "Last Updated"]
    rows = []
    for it in items:
        pwd_display = it.get("password", "")
        rows.append([
            it.get("id", ""),
            it.get("name", ""),
            it.get("username", ""),
            pwd_display,
            it.get("auth_key", ""),
            it.get("website", ""),
            it.get("notes", ""),
            fmt_updated(it.get("updated_at", "")),
        ])
    print_table(rows, headers)

def search_entries(db):
    keyword = input("Enter keyword (name/username/website/notes): ").strip().lower()
    if not keyword:
        print("Keyword cannot be empty.")
        return
    results = []
    for it in db.get("items", []):
        haystack = " ".join([
            str(it.get("name", "")),
            str(it.get("username", "")),
            str(it.get("website", "")),
            str(it.get("notes", "")),
        ]).lower()
        if keyword in haystack:
            results.append(it)
    if not results:
        print("No matching entries.")
        return
    headers = ["ID", "Name", "Username", "Website", "Notes", "Last Updated"]
    rows = [[it["id"], it["name"], it["username"], it["website"], it["notes"], fmt_updated(it.get("updated_at",""))] for it in results]
    print_table(rows, headers)

def edit_entry(db):
    try:
        eid = int(input("Enter ID to edit: ").strip())
    except ValueError:
        print("Invalid ID.")
        return
    it = find_by_id(db, eid)
    if not it:
        print("Entry not found.")
        return

    print("Leave a field blank to keep current value.")
    print(f"Current Name: {it.get('name','')}")
    name = input("New Name: ").strip()

    print(f"Current Username: {it.get('username','')}")
    username = input("New Username: ").strip()

    print("Change password? (y/N): ", end="")
    if input().strip().lower() == "y":
        password = getpass("New Password: ").strip()
    else:
        password = ""

    print(f"Current Auth Key: {it.get('auth_key','')}")
    auth_key = input("New Auth Key: ").strip()

    print(f"Current Website: {it.get('website','')}")
    website = input("New Website: ").strip()

    print(f"Current Notes: {it.get('notes','')}")
    notes = input("New Notes: ").strip()

    changed = False
    if name: it["name"] = name; changed = True
    if username: it["username"] = username; changed = True
    if password: it["password"] = password; changed = True
    if auth_key: it["auth_key"] = auth_key; changed = True
    if website: it["website"] = website; changed = True
    if notes: it["notes"] = notes; changed = True

    if changed:
        it["updated_at"] = now_iso()
        save_db(db)
        print("✅ Entry updated.")
    else:
        print("No changes made.")

def delete_entry(db):
    try:
        eid = int(input("Enter ID to delete: ").strip())
    except ValueError:
        print("Invalid ID.")
        return
    it = find_by_id(db, eid)
    if not it:
        print("Entry not found.")
        return
    confirm = input(f"Delete '{it.get('name','')}' (ID {eid})? (y/N): ").strip().lower()
    if confirm == "y":
        db["items"] = [x for x in db["items"] if x.get("id") != eid]
        save_db(db)
        print("🗑️ Entry deleted.")
    else:
        print("Deletion cancelled.")


# --------------- Menu ----------------
def menu_loop():
    while True:
        print("\n=== Password Manager ===")
        print("1. Add entry")
        print("2. View entries (show passwords)")
        print("3. Search entries")
        print("4. Edit entry")
        print("5. Delete entry")
        print("6. Exit")
        choice = input("Choose an option: ").strip()

        db = load_db()

        if choice == "1":
            add_entry(db); pause()
        elif choice == "2":
            list_entries(db); pause()
        elif choice == "3":
            search_entries(db); pause()
        elif choice == "4":
            edit_entry(db); pause()
        elif choice == "5":
            delete_entry(db); pause()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice."); pause()


# --------------- Main ----------------
def main():
    ensure_registered()
    login()
    load_db()
    menu_loop()

if __name__ == "__main__":
    main()
