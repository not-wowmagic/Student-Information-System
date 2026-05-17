# Enchong Dee University Student Information System

A desktop app for managing student records, grades, schedules, announcements, events, and reports. Students can check their own information. Admins can manage school data in one place.

## Features

### For Students
- Log in with your account
- View grades and subject list
- Check schedule, announcements, and events
- Update account settings

### For Administrators
- Search and manage student records
- Add, edit, and delete students
- Manage subjects, announcements, and events
- Update grades
- Export reports as PDF

## How to Run

Windows users can usually start the app by double-clicking main.py.

If that does not work, open a terminal in the project root and run:

```bash
python --version
python -m pip install ttkbootstrap pillow fpdf bcrypt
python src/main.py
```

Use Python 3.11.x.

The app needs `ttkbootstrap`, `pillow`, `fpdf`, and `bcrypt`.

The app creates its SQLite database and sample records on first launch. It also creates `data/login_credentials.json` when Remember me is used.

## Troubleshooting

If you see `ModuleNotFoundError: No module named 'ttkbootstrap'`, `bcrypt`, `PIL`, or `fpdf`, the packages are missing. Run the install command again with the same Python you use to start the app.

If you see `ModuleNotFoundError: No module named 'constants'`, you started the app from the wrong folder. Go back to the project root and run `python src/main.py`.

If the app opens and closes right away, the terminal has the real error. A missing module means a package problem. A missing image file means the `assets` folder is wrong or incomplete.

If the login window shows no image or icon, check that `assets/edu-icon.png` or `assets/edu1.png` exists.

If `pip` is not recognized, use:

```bash
py -3.11 -m pip install ttkbootstrap pillow fpdf bcrypt
```

If login still fails, make sure you are using the project root, not the `src` folder, and check whether the database was created.