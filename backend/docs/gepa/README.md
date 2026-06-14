# GEPA Guide

Folder ini menjelaskan **Step 5: Jalankan GEPA** dalam alur DSPy + GEPA.

## Apa Yang Terjadi Di Step 5

Di step ini, GEPA mulai bekerja untuk mencoba memperbaiki program DSPy berdasarkan:

- `trainset`
- `metric`
- model yang sudah dikonfigurasi

Pertanyaan yang dijawab step ini:

> "Kalau instruksi/programnya diutak-atik sedikit, adakah versi yang nilainya lebih bagus?"

## Hal Penting Yang Harus Dipahami

GEPA **bukan**:

- training model dari nol
- fine-tuning model
- mengganti model dasar

GEPA itu lebih mirip:

- mencoba versi instruksi yang berbeda
- melihat hasilnya
- menilai hasil itu dengan scorer
- memilih versi yang lebih baik

Jadi GEPA memperbaiki **cara kita memberi instruksi ke model**, bukan melatih model baru.

## Intuisi Sederhana

Bayangkan kamu punya penulis.

Kamu tidak mengganti otaknya.
Kamu hanya mengubah cara briefing-nya:

- brief versi A
- brief versi B
- brief versi C

Lalu kamu nilai:

- mana yang paling jelas
- mana yang paling relevan
- mana yang paling natural

GEPA melakukan hal yang mirip, tapi secara sistematis.

## File Yang Terlibat

### [optimize_gepa.py](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/scripts/optimize_gepa.py:1)

Ini file utama tempat GEPA dijalankan.

Bagian pentingnya:

- membuat `optimizer = dspy.GEPA(...)`
- memanggil `optimizer.compile(...)`
- memberi `trainset` dan `valset`
- mengevaluasi hasil optimized

Kalau mau tahu GEPA dijalankan di mana, lihat file ini.

### [twitter_dspy_program.py](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/app/prompts/twitter_dspy_program.py:1)

Ini program DSPy yang akan dioptimasi oleh GEPA.

GEPA tidak bekerja di ruang kosong.
Dia bekerja terhadap program ini.

Artinya:

- input program ditentukan di sini
- struktur output ditentukan di sini
- kualitas akhirnya tetap diukur dari perilaku program ini

### [gepa_examples.py](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/app/prompts/datasets/gepa_examples.py:1)

Ini loader dataset train/val.

GEPA terutama memakai:

- `trainset` untuk mencoba improve
- `valset` untuk cek hasilnya

### [scoring/README.md](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/app/prompts/scoring/README.md:1)

Scoring adalah "guru" yang memberi nilai ke setiap output.

GEPA butuh scorer karena tanpa metric, dia tidak tahu:

- versi mana yang lebih bagus
- versi mana yang lebih buruk

### [baseline/README.md](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/docs/baseline/README.md:1)

Baseline dipakai sebagai pembanding awal.

Setelah GEPA jalan, hasil optimized akan dibandingkan dengan baseline.

## Baris Penting Di `optimize_gepa.py`

Bagian inti step ini secara konsep adalah:

```python
optimizer = dspy.GEPA(
    metric=twitter_quality_metric,
    max_metric_calls=max_metric_calls,
    reflection_lm=lm,
)
```

dan

```python
optimized_program = optimizer.compile(
    student=TwitterContentProgram(),
    trainset=trainset,
    valset=valset,
)
```

## Arti Masing-Masing Bagian

### `dspy.GEPA(...)`

Ini membuat optimizer GEPA.

Kita memberi tahu GEPA:

- `metric`
  artinya aturan nilai bagus itu apa
- `max_metric_calls`
  artinya berapa kali GEPA boleh mencoba dan menilai
- `reflection_lm`
  artinya model mana yang dipakai selama proses optimasi

### `student=TwitterContentProgram()`

Ini program yang mau diperbaiki.

GEPA akan mencoba memperbaiki performa program ini.

### `trainset=trainset`

Ini data latihan.

GEPA melihat contoh-contoh ini untuk mencari cara agar output lebih cocok dengan scorer.

### `valset=valset`

Ini data validasi.

GEPA bisa memakainya untuk mengecek apakah perbaikannya lebih stabil, bukan cuma cocok pada data latihan.

## Alur Kerja GEPA Secara Sederhana

Urutannya seperti ini:

1. mulai dari program awal
2. lihat `trainset`
3. generate output
4. nilai output dengan `metric`
5. coba ubah instruksi/program
6. generate lagi
7. nilai lagi
8. pilih versi yang lebih baik

Jadi GEPA itu iteratif.

Dia tidak langsung "tahu jawaban benar".
Dia mencoba, dinilai, lalu mencoba lagi.

## Kenapa `metric` Penting Banget

GEPA hanya akan improve ke arah yang kamu ukur.

Kalau scorer kamu menghargai:

- clarity
- relevance
- naturalness

maka GEPA akan berusaha bergerak ke sana.

Kalau scorer kamu jelek, GEPA bisa mengoptimasi hal yang salah.

Jadi kualitas GEPA sangat tergantung pada kualitas:

- dataset
- scorer
- program awal

## Kenapa Ini Bukan Training Model

Saat GEPA jalan:

- model dasarnya tetap sama
- bobot model tidak berubah
- yang berubah adalah cara program/instruksi dipakai

Jadi kalau sebelumnya kamu bingung:

> "Apakah GEPA melatih model?"

Jawabannya:

> Tidak. GEPA mengoptimasi program/prompt, bukan melatih model baru.

## Apa Output Dari Step 5

Output utama step ini adalah:

- `optimized_program`

Itu artinya:

- kita punya versi program hasil GEPA
- versi ini nanti diuji lagi
- lalu dibandingkan dengan baseline

Jadi step 5 belum final.
Dia menghasilkan kandidat versi yang diharapkan lebih baik.

## Hubungan Step 4 Dan Step 5

Step 4:

- hitung baseline dulu

Step 5:

- jalankan GEPA untuk mencari versi yang lebih baik

Tanpa step 4, kamu tidak punya pembanding.
Tanpa step 5, kamu tidak punya proses improve.

## Apa Yang Harus Kamu Lihat Saat Belajar

Kalau mau paham step ini, baca urut begini:

1. [optimize_gepa.py](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/scripts/optimize_gepa.py:1)
2. [twitter_dspy_program.py](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/app/prompts/twitter_dspy_program.py:1)
3. [gepa_examples.py](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/app/prompts/datasets/gepa_examples.py:1)
4. [scoring/README.md](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/app/prompts/scoring/README.md:1)

## Ringkasan Singkat

Ingat kalimat ini:

> GEPA mencoba beberapa versi instruksi/program dan memilih yang nilainya lebih baik menurut metric.

Jadi step 5 menjawab:

> "Kalau kita ubah cara kita briefing ke model, bisakah hasilnya jadi lebih bagus?"
