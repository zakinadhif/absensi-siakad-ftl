# absensi-siakad-ftl
Faster than light absensi siakad

## Usage

Mengabsen masuk luring:
```
python3 main.py -m masuk -d luring <email> <password>
```

Mengambil status absen dari server:
```
python3 main.py --get-status <email> <password>
```

## Session File

Percepat absen menggunakan session file:
```
python3 main.py --generate-session my-session.pkl <email> <password>
python3 main.py --use-session my-session.pkl -m masuk -d luring
```

Percepat lagi dengan `--skip-session-check`

## Automasisasi dengan cronjob
```
*/15 6 * * 1-5 /usr/bin/python3 <absolute_path_to_script> --use-session <absolute_path_to_session_file> -m masuk -d luring --skip-session-check > /tmp/absen.txt
```

## Full Usage Description
```
usage: main.py [-h] [-d DALU] [-m MODE] [--izin PATH] [-s] [--use-session PATH] [--generate-session PATH] [--skip-session-check] [username] [password]

Isi presensi pada https://siswa.smktelkom-mlg.sch.id dengan kecepatan cahaya

positional arguments:
  username              username siakad
  password              password siakad

optional arguments:
  -h, --help            show this help message and exit
  -d DALU, --dalu DALU  pilih daring atau luring jika masuk
  -m MODE, --mode MODE  pilih presensi yang mau diisi
  --izin PATH           path ke foto izin jika dispensasi, sakit atau ijin
  -s, --get-status      get status presensi dari siakad
  --use-session PATH    gunakan session yang sudah ada atau buat kembali
  --generate-session PATH
  --skip-session-check  percepat proses absen dengan melewati proses cek kevalidan sesi
```
