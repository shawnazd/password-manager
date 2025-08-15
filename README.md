
# 🔐 Personal Password Manager

A simple and secure **Password Manager** to store and manage your passwords safely in a JSON file.  

---

## Features ✨

- Add, edit, and delete password entries  
- Store details like:  
  - Name  
  - Username  
  - Password  
  - Authentication key  
  - Website URL  
  - Notes  
- View entries with **passwords shown**  
- Tracks **last updated date** for each entry  
- Master password protected 🔑  
- Data automatically saved in a JSON file  

---

## Installation 💻

1. Clone the repository:
```bash
git clone https://github.com/shawnazd/password-manager.git
````

2. Navigate to the project folder:

```bash
cd password-manager
```

3. Run the project:

```bash
python password_manager.py
```

> On first run, you will be asked to create a **Master Password**. This is required to access all entries.

---

## Usage 📌

1. **Add Entry**: Add new password details.
2. **View Entries (Show Passwords)**: View all saved entries with proper alignment and last updated date.
3. **Edit Entry**: Update username, password, URL, authentication key, or notes.
4. **Delete Entry**: Remove an entry by its ID.

> All data is stored securely in a JSON file (`passwords.json`).

---

## Security ⚠️

* Never share your **Master Password**.
* Passwords are saved in the JSON file, protected by the Master Password access.
* Do **not** upload the JSON file to public repositories.

---

## Contributing 🤝

Feel free to fork the repo and submit pull requests to improve the project!

---

## License 📄

This project is open-source and free to use.


