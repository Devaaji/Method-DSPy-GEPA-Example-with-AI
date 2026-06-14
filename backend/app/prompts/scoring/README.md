# Scoring Guide

Folder ini berisi evaluator untuk menilai apakah output tweet dari DSPy/GEPA itu bagus atau belum.

## Tujuan

Scoring dipakai untuk menjawab pertanyaan:

- Apakah output relevan dengan topik?
- Apakah pembukanya menarik?
- Apakah tulisannya jelas?
- Apakah bahasanya natural?
- Apakah output patuh pada constraint?
- Apakah output mengikuti gaya contoh yang baik?
- Apakah output menghindari pola yang jelek?

GEPA tidak tahu sendiri arti "bagus". Folder ini adalah tempat kita mendefinisikan aturan itu.

## Alur Besar

Urutannya seperti ini:

1. `evaluator.py` menerima `example` dan `prediction`
2. `utils.py` mengekstrak tweet dan field tambahan
3. setiap file scoring menghitung satu aspek
4. `evaluator.py` menggabungkan semua score
5. hasil akhir dikembalikan sebagai:
   - `overall_score`
   - `aspect_scores`
   - `notes`

## File Overview

### `evaluator.py`

File utama untuk scoring.

Tugasnya:
- mengambil data dari `example`
- memanggil semua scorer per aspek
- menggabungkan hasil menjadi `overall_score`
- mengembalikan notes evaluasi

Kalau kamu mau paham alur besar dulu, mulai dari file ini.

### `constraints.py`

Menilai apakah output:
- sesuai jumlah draft yang diminta
- tidak melebihi `max_chars`
- tidak kebanyakan hashtag
- menghormati `include_hashtags`

Ini menjawab:
"Apakah output patuh ke aturan teknis?"

### `relevance.py`

Menilai apakah isi tweet masih nyambung ke:
- `topic`
- `audience`

Ini menjawab:
"Apakah output benar-benar membahas hal yang diminta?"

### `clarity.py`

Menilai apakah tweet:
- cukup ringkas
- gampang dibaca
- punya struktur yang enak di-scan

Ini menjawab:
"Apakah output mudah dipahami dengan cepat?"

### `hook.py`

Menilai apakah pembuka tweet cukup kuat.

Hal yang dicek misalnya:
- ada pola hook
- ada pertanyaan
- ada angka
- ada kontras

Ini menjawab:
"Apakah opening-nya cukup menarik untuk berhenti scroll?"

### `naturalness.py`

Menilai apakah bahasa terasa:
- natural
- tidak generik
- tidak terlalu repetitif
- tidak terlalu penuh emoji atau hype

Ini menjawab:
"Apakah output terasa seperti tulisan manusia?"

### `reference_fit.py`

Menilai apakah output cukup dekat dengan kualitas `reference_posts`.

Reference posts dipakai sebagai contoh:
- gaya yang diinginkan
- tingkat spesifik yang diinginkan
- nada yang terasa benar

Ini menjawab:
"Apakah hasilnya mendekati contoh post yang kita anggap bagus?"

### `avoidance.py`

Menilai apakah output berhasil menghindari hal-hal dalam `avoid`.

Contoh:
- buzzword
- generic phrasing
- terlalu banyak hashtag
- terlalu banyak emoji
- pola salesy

Ini menjawab:
"Apakah output menghindari pola jelek yang memang mau kita hindari?"

### `utils.py`

Helper kecil untuk:
- `extract_tweets`
- `extract_list`

Supaya parsing tidak numpuk di evaluator utama.

### `constants.py`

Berisi konstanta seperti:
- `GENERIC_PHRASES`
- `HOOK_WORDS`

Dipakai ulang oleh beberapa scorer.

### `__init__.py`

Entry point package.

Ini membuat import seperti:

```python
from app.prompts.scoring import evaluate_twitter_output
```

tetap bisa dipakai.

## Aspek Yang Dinilai

Saat ini evaluator menghitung:

- `relevance`
- `hook`
- `clarity`
- `naturalness`
- `constraint_fit`
- `reference_fit`
- `avoidance`

## Bobot Score Saat Ini

Bobot total saat ini:

- `relevance`: 0.20
- `hook`: 0.18
- `clarity`: 0.16
- `naturalness`: 0.15
- `constraint_fit`: 0.14
- `reference_fit`: 0.10
- `avoidance`: 0.07

Kalau mau mengubah arti "bagus", biasanya kamu akan mengubah:
- aturan di scorer per aspek
- atau bobot di `evaluator.py`

## Cara Baca Folder Ini

Kalau kamu belajar dari nol, baca urut begini:

1. `evaluator.py`
2. `constraints.py`
3. `relevance.py`
4. `clarity.py`
5. `hook.py`
6. `naturalness.py`
7. `reference_fit.py`
8. `avoidance.py`

## Kapan Ubah Apa

Kalau masalahnya output:

- terlalu panjang atau hashtag berlebihan
  ubah `constraints.py`
- keluar topik atau tidak cocok audience
  ubah `relevance.py`
- susah dibaca
  ubah `clarity.py`
- opening lemah
  ubah `hook.py`
- terlalu AI / terlalu generik
  ubah `naturalness.py`
- tidak mirip kualitas contoh bagus
  ubah `reference_fit.py`
- masih melanggar pola yang dilarang
  ubah `avoidance.py`

## Ringkasan Singkat

Ingat cara mikirnya:

- dataset memberi contoh tugas
- DSPy menghasilkan output
- folder scoring menilai hasilnya
- GEPA memakai score itu untuk mencoba improve prompt/program

Jadi folder ini adalah "guru penilai" di sistem DSPy + GEPA kamu.
