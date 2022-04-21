"""
    Automatic attendance fill core module

    This module contains functions essential for the fillng action
"""

from enum import Enum
import json
import argparse
import os

import pickle
import requests

ENDPOINTS = {
    "welcome_page": "https://siswa.smktelkom-mlg.sch.id/welcome",
    "presence_status": "https://siswa.smktelkom-mlg.sch.id/welcome/get_status_hadir",
    "presence_fill": "https://siswa.smktelkom-mlg.sch.id/presnow/chsts",
    "presence_page": "https://siswa.smktelkom-mlg.sch.id/presnow",
    "login": "https://siswa.smktelkom-mlg.sch.id/login/act_login",
    "login_page": "https://siswa.smktelkom-mlg.sch.id/login"
}

SESSION_FILENAME = "session.pkl"

class Dalu(Enum):
    """ Dalu enum for choosing between Daring and Luring """
    DARING = 0
    LURING = 1

def dalu_to_str(dalu: Dalu) -> str:
    """ Converts Dalu enum to valid post-able string argument """
    if dalu == Dalu.DARING:
        return "daring"
    if dalu == Dalu.LURING:
        return "luring"
    raise RuntimeError("Invalid Dalu enum value")

def post_attendance(session: requests.Session, dalu: Dalu):
    """ Do a post request to fill the attendance """
    headers = {
        "Referer": ENDPOINTS["presence_page"]
    }

    params = {
        "ijin": (None, "M", None),
        "dalu": (None, dalu_to_str(dalu), None),
    }

    return session.post(
        url = ENDPOINTS["presence_fill"],
        files = params,
        headers = headers,
    )

def load_presence_page(session: requests.Session):
    """ Load the presence page in order to get attendance token """
    headers = {
        "Referer": ENDPOINTS["welcome_page"]
    }

    r = session.get(
        url = ENDPOINTS["presence_page"],
        headers = headers,
        allow_redirects=False
    )

    if r.status_code == 302:
        raise RuntimeError("Gagal untuk melakukan operasi: Request redirected, cek username & password anda")

def try_fill_attendance(dalu: Dalu, session: requests.Session):
    """
        Tries to fill the attendance form for the user
    """

    print("Attempting to load token...")
    load_presence_page(session)

    print("Attempting fill presence...")
    post_attendance(session, dalu)

    presence_status = get_status_hadir(session)
    print("Presence:", presence_status)

    return presence_status

def try_login(email, password):
    s = requests.Session()

    s.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"})

    r = s.post(ENDPOINTS["login"], data={
        "email": email,
        "password": password,
        "token": "",
        "g-recaptcha-response": ""
    })

    return s if r.json()["log"]["status"] == 1 else False

def get_status_hadir(s: requests.Session):
    r = s.get(ENDPOINTS["presence_status"], allow_redirects=False)

    if r.status_code == 302:
        raise RuntimeError("Gagal untuk mengambil status hadir: Request redirected, cek username & password anda")

    return r.json()["status_presensi"][0].lower()

def is_logged_in(s: requests.Session):
    r = s.get(ENDPOINTS["presence_status"], allow_redirects=False)

    return r.status_code == 200

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Isi presensi pada https://siswa.smktelkom-mlg.sch.id dengan kecepatan cahaya",
    )
    parser.add_argument("username", help="username siakad", nargs="?")
    parser.add_argument("password", help="password siakad", nargs="?")
    parser.add_argument("-d", "--dalu", choices=["daring", "luring"], metavar="DALU", help="pilih daring atau luring jika masuk")
    parser.add_argument("-m", "--mode", choices=["masuk", "ijin", "dispensasi", "sakit"], metavar="MODE", help="pilih presensi yang mau diisi")
    parser.add_argument("--izin", help="path ke foto izin jika dispensasi, sakit atau ijin", metavar="PATH")
    parser.add_argument("-s", "--get-status", help="get status presensi dari siakad", action="store_true")
    parser.add_argument("--use-session", help="gunakan session yang sudah ada atau buat kembali", metavar="PATH", default=False)
    parser.add_argument("--generate-session", metavar="PATH", default=False)
    parser.add_argument("--skip-session-check", action="store_true", help="percepat proses absen dengan melewati proses cek kevalidan sesi")

    args = parser.parse_args()
    session = None

    # `--generate-session [path]`
    if args.generate_session:
        if args.username is None or args.password is None:
            parser.print_usage()
            print("Parameter username dan password kosong")
            exit(1)

        session = try_login(args.username, args.password)

        # Ensure session is valid
        if not session:
            print("Gagal membuat file sesi, cek username dan password anda")
            exit(1)

        with open(args.generate_session, "wb") as session_file:
            pickle.dump(session, session_file)
        exit()

    # `--use-session`
    if args.use_session:
        if not os.path.isfile(args.use_session):
            print(f"File sesi {args.use_session} tidak ada, anda harus membuatnya terlebih dahulu dengan --generate-session [PATH]")
            exit(1)

        with open(args.use_session, "rb") as session_file:
            session = pickle.load(session_file)

        if not args.skip_session_check and not is_logged_in(session):
            print("Gagal login, coba buat kembali file sesi anda")
            exit(1)
    else:
        if args.username is None or args.password is None:
            parser.print_usage()
            print("Parameter username dan password kosong")
            exit(1)

        session = try_login(args.username, args.password)

        if not session:
            print("Gagal login, cek username dan password anda")

    # `--get-status`
    if args.get_status == True:
        status_hadir = get_status_hadir(session)
        print("Kehadiran:", status_hadir)
        exit(0 if "masuk" in status_hadir else -1)

    # `-m [masuk|izin|dispensasi|sakit]` `-d [daring|luring]`
    if args.mode:
        if args.mode == "masuk":
            if not args.dalu:
                parser.print_usage()
                print("Gagal: parameter dalu kosong, isi luring atau daring")
                exit(1)

            try_fill_attendance(Dalu[args.dalu.upper()], session)
        else:
            print("Presensi dengan mode selain masuk belum didukung")

    # update session file if `--use-session` is specified
    if args.use_session:
        with open(args.use_session, "wb") as session_file:
            pickle.dump(session, session_file)
        exit()
