# Baseline Guide

Folder ini menjelaskan **Step 4: Buat baseline** dalam alur DSPy + GEPA.

## Apa Itu Baseline

Baseline adalah:

- versi program **sebelum** dioptimasi GEPA
- nilai awal yang dipakai sebagai pembanding

Pertanyaan yang dijawab baseline:

> "Kalau program sekarang dipakai apa adanya, nilainya berapa?"

Kalau tidak ada baseline, kita tidak tahu apakah hasil setelah GEPA:

- benar-benar naik
- tetap sama
- atau malah turun

## Intuisi Sederhana

Bayangkan seperti ini:

1. kita punya murid
2. sebelum diberi latihan tambahan, kita kasih ujian dulu
3. nilai ujian pertama itu adalah **baseline**
4. setelah dilatih, kita ujian lagi
5. baru kita bandingkan

Dalam project ini:

- `baseline_program` = murid sebelum dilatih GEPA
- `optimized_program` = murid setelah GEPA
- `valset` = soal ujian
- `scoring` = guru penilai

## File Yang Terlibat

### [optimize_gepa.py](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/scripts/optimize_gepa.py:1)

Ini file utama proses baseline dan optimasi.

Bagian pentingnya:

- load model dan konfigurasi
- load dataset train/val
- buat `baseline_program`
- jalankan baseline di `valset`
- jalankan GEPA
- bandingkan baseline vs optimized
- simpan hasil ke `optimized_prompt.json`

Kalau mau tahu baseline dihitung di mana, mulai dari file ini.

### [twitter_dspy_program.py](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/app/prompts/twitter_dspy_program.py:1)

Ini definisi program DSPy yang dipakai sebagai baseline.

Isinya menjelaskan:

- input apa saja yang masuk
- output apa yang dihasilkan
- bagaimana DSPy memanggil model

Kalau di baseline ada baris:

```python
baseline_program = TwitterContentProgram()
```

berarti program awal itu datang dari file ini.

### [gepa_examples.py](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/app/prompts/datasets/gepa_examples.py:1)

Ini loader dataset.

Tugasnya:

- menggabungkan dataset train dan val
- memperkaya contoh dengan:
  - `reference_posts`
  - `quality_criteria`
  - `avoid`
- mengubah dict biasa menjadi `dspy.Example`

Baseline butuh file ini karena baseline harus diuji pada data nyata.

### [gepa_english.py](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/app/prompts/datasets/gepa_english.py:1)

Berisi dataset English untuk:

- `ENGLISH_TRAIN_EXAMPLES`
- `ENGLISH_VAL_EXAMPLES`

### [gepa_indonesian.py](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/app/prompts/datasets/gepa_indonesian.py:1)

Berisi dataset Indonesian untuk:

- `INDONESIAN_TRAIN_EXAMPLES`
- `INDONESIAN_VAL_EXAMPLES`

Kedua file ini penting karena baseline dinilai pada `valset`, bukan asal data apa saja.

### [scoring/README.md](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/app/prompts/scoring/README.md:1)

Folder scoring adalah tempat aturan penilaian didefinisikan.

Baseline tidak punya arti tanpa scorer.

Scorer menentukan:

- relevance
- hook
- clarity
- naturalness
- constraint_fit
- reference_fit
- avoidance

### [optimized_prompt.json](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/app/prompts/optimized_prompt.json:1)

Ini hasil akhir eksperimen.

Di sini kamu bisa lihat:

- `baseline_validation_score`
- `optimized_validation_score`
- `score_delta`
- perbandingan output baseline vs optimized

Kalau kamu ingin melihat hasil baseline secara nyata, lihat file ini.

## Alur Baseline Di Code

Urutannya seperti ini:

1. load dataset
2. pisahkan `trainset` dan `valset`
3. buat baseline program
4. jalankan baseline program ke `valset`
5. nilai hasilnya dengan scorer
6. hitung rata-rata score

Bagian penting di [optimize_gepa.py](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/scripts/optimize_gepa.py:1):

```python
baseline_program = TwitterContentProgram()
baseline_score, baseline_previews = evaluate_program(baseline_program, valset)
```

Arti dua baris itu:

- buat versi awal program
- tes dulu di validation set
- simpan nilainya

Itulah baseline.

## Fungsi Penting Di `optimize_gepa.py`

### `example_inputs(example)`

Tugas:

- mengambil field dari dataset example
- mengubahnya ke bentuk input yang siap dikirim ke program DSPy

Kenapa penting:

- baseline dan optimized sama-sama pakai input ini
- jadi pembandingnya fair

### `evaluate_program(program, dataset)`

Tugas:

- jalankan satu program ke semua example dalam dataset
- score tiap output
- kumpulkan preview dan notes
- hitung rata-rata

Kenapa penting:

- inilah fungsi yang benar-benar menghitung baseline

Outputnya:

- `average score`
- `previews per topic`

### `build_preview_comparison(...)`

Tugas:

- membandingkan baseline vs optimized per topik

Kenapa penting:

- kamu bisa lihat bukan cuma score total
- tapi juga aspek mana yang naik atau turun

## Kenapa Baseline Diuji di `valset`

Karena kita ingin baseline dan optimized dinilai di soal yang sama.

Kalau:

- baseline diuji di data A
- optimized diuji di data B

maka hasilnya tidak fair.

Makanya:

- baseline diuji di `valset`
- optimized juga diuji di `valset`

Jadi pembandingnya apple-to-apple.

## Apa Yang Harus Kamu Lihat Saat Belajar

Kalau mau paham baseline tanpa bingung, baca urut begini:

1. [optimize_gepa.py](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/scripts/optimize_gepa.py:1)
2. [twitter_dspy_program.py](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/app/prompts/twitter_dspy_program.py:1)
3. [gepa_examples.py](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/app/prompts/datasets/gepa_examples.py:1)
4. [scoring/README.md](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/app/prompts/scoring/README.md:1)
5. [optimized_prompt.json](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/app/prompts/optimized_prompt.json:1)

## Ringkasan Singkat

Ingat kalimat ini:

> Baseline adalah nilai awal program sebelum GEPA mencoba memperbaikinya.

Jadi baseline dipakai untuk menjawab:

> "Sebelum dioptimasi, performanya sekarang sebenarnya seberapa bagus?"

Kalau setelah GEPA nilainya lebih tinggi daripada baseline, baru kita punya alasan untuk bilang:

> "Ya, optimasinya membantu."
