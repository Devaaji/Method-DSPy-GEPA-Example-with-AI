from __future__ import annotations

from typing import Any


COMMON_QUALITY_CRITERIA = [
    "Bahasa Indonesia natural, tidak kaku, tidak terlalu formal.",
    "Ada satu ide utama yang jelas.",
    "Tidak terdengar seperti template AI.",
    "Tidak terlalu promosi atau hard-selling.",
    "Ada insight praktis, bukan sekadar motivasi umum.",
    "Kalimat pendek, mudah dibaca di Twitter/X.",
]


INDONESIAN_TRAIN_EXAMPLES: list[dict[str, Any]] = [
    {
        "topic": "Cara founder menjaga konsistensi konten tanpa kehilangan kualitas",
        "tone": "friendly",
        "audience": "founder Indonesia",
        "language": "Indonesian",
        "count": 1,
        "max_chars": 280,
        "include_hashtags": True,
        "quality_criteria": COMMON_QUALITY_CRITERIA + [
            "Berikan sudut pandang yang relatable untuk founder sibuk.",
            "Jangan menyuruh posting setiap hari tanpa konteks.",
        ],
        "avoid": [
            "Konten generik seperti 'konsistensi adalah kunci'.",
            "Terlalu banyak emoji.",
            "Hashtag lebih dari 2.",
        ],
        "reference_posts": [
            "Founder sering gagal konsisten bukan karena malas, tapi karena semua konten harus terasa “sempurna”. Mulai dari ide kecil: pelajaran minggu ini, keputusan sulit, atau insight dari customer. Konsisten dulu, polish sambil jalan. #FounderIndonesia"
        ],
    },
    {
        "topic": "Cara tim marketing kecil tetap konsisten posting tanpa burnout",
        "tone": "supportive",
        "audience": "tim marketing Indonesia",
        "language": "Indonesian",
        "count": 2,
        "max_chars": 220,
        "include_hashtags": False,
        "quality_criteria": COMMON_QUALITY_CRITERIA + [
            "Tekankan sistem kerja ringan, bukan menambah beban tim.",
            "Output harus terasa empatik.",
        ],
        "avoid": [
            "Menyalahkan tim karena tidak konsisten.",
            "Saran terlalu abstrak.",
        ],
        "reference_posts": [
            "Tim kecil nggak harus produksi konten dari nol setiap hari. Pecah 1 ide besar jadi beberapa format: insight, checklist, contoh kasus, dan opini singkat. Konsistensi lebih mudah kalau sistemnya ringan.",
            "Burnout sering muncul karena semua konten diperlakukan seperti campaign besar. Padahal beberapa post cukup menjawab satu pertanyaan kecil dari audiens. Simpel, relevan, selesai.",
        ],
    },
    {
        "topic": "Mengapa approval konten penting sebelum auto publish di banyak channel",
        "tone": "professional",
        "audience": "social media managers Indonesia",
        "language": "Indonesian",
        "count": 1,
        "max_chars": 240,
        "include_hashtags": True,
        "quality_criteria": COMMON_QUALITY_CRITERIA + [
            "Jelaskan risiko auto-publish secara tenang dan profesional.",
            "Beri alasan kenapa approval flow penting.",
        ],
        "avoid": [
            "Menakut-nakuti secara berlebihan.",
            "Bahasa terlalu teknis.",
        ],
        "reference_posts": [
            "Auto-publish itu membantu, tapi tanpa approval flow risikonya besar: salah konteks, salah channel, atau tone tidak sesuai brand. Approval bukan memperlambat kerja, tapi menjaga kualitas sebelum konten jalan otomatis. #SocialMedia"
        ],
    },
    {
        "topic": "Cara founder personal branding tanpa terdengar terlalu pencitraan",
        "tone": "casual",
        "audience": "startup founders Indonesia",
        "language": "Indonesian",
        "count": 2,
        "max_chars": 220,
        "include_hashtags": False,
        "quality_criteria": COMMON_QUALITY_CRITERIA + [
            "Buat founder terasa manusiawi, bukan sedang jual diri.",
            "Dorong storytelling dari proses nyata.",
        ],
        "avoid": [
            "Nada terlalu sok bijak.",
            "Klaim berlebihan tentang kesuksesan.",
        ],
        "reference_posts": [
            "Personal branding founder nggak harus selalu tentang menang besar. Kadang justru lebih kuat saat cerita soal keputusan sulit, trade-off, atau hal yang baru dipelajari minggu ini.",
            "Biar nggak terdengar pencitraan, jangan cuma bilang “kami hebat”. Ceritakan prosesnya: apa masalahnya, kenapa pilih jalan itu, dan apa yang berubah setelahnya.",
        ],
    },
    {
        "topic": "Cara menulis thread edukatif yang terasa ringan tapi tetap bernilai",
        "tone": "educational",
        "audience": "content creators Indonesia",
        "language": "Indonesian",
        "count": 2,
        "max_chars": 250,
        "include_hashtags": True,
        "quality_criteria": COMMON_QUALITY_CRITERIA + [
            "Berikan prinsip menulis thread yang mudah dipraktikkan.",
            "Tidak perlu membuat thread terlalu panjang.",
        ],
        "avoid": [
            "Opening clickbait kosong.",
            "Tips terlalu umum seperti 'buat konten berkualitas'.",
        ],
        "reference_posts": [
            "Thread edukatif yang enak dibaca biasanya punya 1 janji jelas di awal, lalu tiap poin menjawab janji itu. Jangan masukkan semua hal yang kamu tahu. Pilih yang paling membantu audiens hari ini. #ContentTips",
            "Biar thread terasa ringan, tulis seperti menjelaskan ke teman kerja: mulai dari masalah, beri contoh, lalu tutup dengan takeaway. Edukatif bukan berarti harus berat. #Creator"
        ],
    },
    {
        "topic": "Mengapa tweet yang terlalu generik biasanya gagal dapat respons",
        "tone": "direct",
        "audience": "solo creators Indonesia",
        "language": "Indonesian",
        "count": 1,
        "max_chars": 220,
        "include_hashtags": False,
        "quality_criteria": COMMON_QUALITY_CRITERIA + [
            "Nada boleh tegas, tapi tidak menghina.",
            "Tunjukkan kenapa specificity penting.",
        ],
        "avoid": [
            "Bahasa kasar.",
            "Menggurui audiens.",
        ],
        "reference_posts": [
            "Tweet generik susah dapat respons karena audiens nggak merasa “ini buat gue”. Ganti nasihat besar dengan situasi spesifik: siapa audiensnya, masalahnya apa, dan momen apa yang sedang mereka alami."
        ],
    },
    {
        "topic": "Cara pakai insight dari komentar audiens untuk bikin konten berikutnya",
        "tone": "helpful",
        "audience": "brand builders Indonesia",
        "language": "Indonesian",
        "count": 2,
        "max_chars": 230,
        "include_hashtags": False,
        "quality_criteria": COMMON_QUALITY_CRITERIA + [
            "Jelaskan cara mengubah komentar jadi ide konten.",
            "Harus terasa praktis untuk brand builder.",
        ],
        "avoid": [
            "Menganggap komentar cuma engagement.",
            "Saran yang terlalu kompleks.",
        ],
        "reference_posts": [
            "Komentar audiens itu bukan cuma engagement. Itu bahan riset gratis. Kalau ada pertanyaan yang berulang, jadikan post. Kalau ada keberatan, jadikan klarifikasi. Kalau ada cerita, jadikan angle baru.",
            "Cara simpel cari ide konten: baca 10 komentar terakhir, tandai pertanyaan, kebingungan, dan kalimat yang emosional. Dari situ biasanya muncul konten yang lebih relevan daripada brainstorming kosong.",
        ],
    },
    {
        "topic": "Cara menyederhanakan ide teknis supaya tetap menarik untuk audience non teknis",
        "tone": "friendly",
        "audience": "technical founders Indonesia",
        "language": "Indonesian",
        "count": 2,
        "max_chars": 250,
        "include_hashtags": True,
        "quality_criteria": COMMON_QUALITY_CRITERIA + [
            "Jangan terlalu banyak jargon teknis.",
            "Gunakan analogi sederhana.",
        ],
        "avoid": [
            "Menjelaskan fitur terlalu detail.",
            "Membuat audiens non-teknis merasa bodoh.",
        ],
        "reference_posts": [
            "Ide teknis jadi lebih menarik kalau dimulai dari masalah manusia, bukan dari arsitektur sistem. Jangan buka dengan “kami pakai X”. Buka dengan “ini masalah yang biasanya bikin tim buang waktu”. #Startup",
            "Kalau audiens non-teknis belum peduli dengan teknologinya, jelaskan dampaknya dulu: lebih cepat, lebih murah, lebih aman, atau lebih mudah dipakai. Detail teknis bisa menyusul. #FounderTips",
        ],
    },
    {
        "topic": "Mengapa founder perlu punya angle opini, bukan cuma update produk",
        "tone": "thoughtful",
        "audience": "early-stage founders Indonesia",
        "language": "Indonesian",
        "count": 1,
        "max_chars": 220,
        "include_hashtags": False,
        "quality_criteria": COMMON_QUALITY_CRITERIA + [
            "Tunjukkan pentingnya sudut pandang founder.",
            "Buat konten terasa reflektif.",
        ],
        "avoid": [
            "Terlalu filosofis.",
            "Menyuruh founder kontroversial tanpa alasan.",
        ],
        "reference_posts": [
            "Update produk memberi tahu orang apa yang kamu bangun. Angle opini memberi tahu kenapa kamu membangunnya. Di tahap awal, orang sering percaya pada cara berpikirmu dulu sebelum percaya pada produknya."
        ],
    },
    {
        "topic": "Cara bikin konten B2B yang tetap manusiawi dan tidak terasa seperti brosur",
        "tone": "practical",
        "audience": "B2B marketers Indonesia",
        "language": "Indonesian",
        "count": 2,
        "max_chars": 230,
        "include_hashtags": False,
        "quality_criteria": COMMON_QUALITY_CRITERIA + [
            "Berikan cara konkret membuat B2B lebih relatable.",
            "Hindari bahasa brosur.",
        ],
        "avoid": [
            "Kata-kata terlalu salesy seperti 'solusi terbaik'.",
            "Klaim tanpa contoh.",
        ],
        "reference_posts": [
            "Konten B2B terasa seperti brosur saat terlalu fokus ke fitur. Coba mulai dari situasi nyata: meeting yang molor, data yang berantakan, approval yang lama. Masalah manusia bikin B2B lebih hidup.",
            "B2B tetap manusiawi kalau kamu menulis untuk orang di balik jabatan. Bukan “perusahaan butuh efisiensi”, tapi “tim kamu capek bolak-balik cek manual”. Lebih dekat, lebih terasa.",
        ],
    },
    {
        "topic": "Cara menilai kualitas caption tanpa cuma bilang bagus atau jelek",
        "tone": "educational",
        "audience": "junior social media specialists Indonesia",
        "language": "Indonesian",
        "count": 2,
        "max_chars": 240,
        "include_hashtags": False,
        "quality_criteria": COMMON_QUALITY_CRITERIA + [
            "Berikan checklist evaluasi caption.",
            "Cocok untuk junior social media specialist.",
        ],
        "avoid": [
            "Feedback subjektif tanpa alasan.",
            "Bahasa terlalu senior atau mengintimidasi.",
        ],
        "reference_posts": [
            "Caption jangan cuma dinilai “bagus” atau “jelek”. Cek 4 hal: hook-nya jelas, pesannya fokus, audiens tahu harus merasa apa, dan CTA-nya masuk akal.",
            "Caption yang baik biasanya punya satu tugas utama. Kalau dalam satu caption kamu ingin edukasi, jualan, branding, dan viral sekaligus, pesan utamanya sering jadi kabur.",
        ],
    },
    {
        "topic": "Cara mengubah satu artikel panjang menjadi beberapa tweet bernilai",
        "tone": "practical",
        "audience": "content repurposers Indonesia",
        "language": "Indonesian",
        "count": 2,
        "max_chars": 230,
        "include_hashtags": False,
        "quality_criteria": COMMON_QUALITY_CRITERIA + [
            "Fokus ke repurposing konten.",
            "Beri langkah yang mudah dipakai.",
        ],
        "avoid": [
            "Menyarankan copy-paste artikel.",
            "Output terasa seperti ringkasan kaku.",
        ],
        "reference_posts": [
            "Satu artikel panjang bisa jadi banyak tweet kalau kamu pecah berdasarkan fungsi: 1 insight utama, 1 contoh, 1 kesalahan umum, 1 checklist, dan 1 opini. Jangan cuma diringkas.",
            "Repurpose yang bagus bukan memotong artikel jadi pendek. Ambil satu ide, ubah konteksnya, lalu tulis ulang supaya cocok dibaca cepat di timeline.",
        ],
    },
    {
        "topic": "Mengapa konten founder yang terlalu rapi kadang terasa jauh",
        "tone": "honest",
        "audience": "startup founders Indonesia",
        "language": "Indonesian",
        "count": 1,
        "max_chars": 220,
        "include_hashtags": False,
        "quality_criteria": COMMON_QUALITY_CRITERIA + [
            "Bahas authenticity tanpa menyuruh oversharing.",
            "Nada jujur dan dewasa.",
        ],
        "avoid": [
            "Menyarankan drama personal.",
            "Menyerang founder yang kontennya polished.",
        ],
        "reference_posts": [
            "Konten founder yang terlalu rapi kadang terasa jauh karena audiens cuma melihat hasil akhir. Sesekali tunjukkan proses berpikir, trade-off, atau keputusan yang belum sempurna. Itu bikin orang lebih percaya."
        ],
    },
    {
        "topic": "Cara membuat CTA yang tidak terasa memaksa",
        "tone": "friendly",
        "audience": "social media marketers Indonesia",
        "language": "Indonesian",
        "count": 2,
        "max_chars": 220,
        "include_hashtags": False,
        "quality_criteria": COMMON_QUALITY_CRITERIA + [
            "CTA harus natural dan relevan.",
            "Tidak terlalu agresif.",
        ],
        "avoid": [
            "CTA seperti 'beli sekarang sebelum terlambat'.",
            "Terlalu banyak tanda seru.",
        ],
        "reference_posts": [
            "CTA nggak harus selalu “klik sekarang”. Kadang cukup ajak audiens mikir: “Pernah ngalamin ini juga?” Kalau kontennya bagus, CTA yang ringan justru terasa lebih natural.",
            "CTA yang enak dibaca biasanya nyambung dengan isi post. Kalau post-nya edukatif, ajak simpan. Kalau post-nya opini, ajak diskusi. Jangan semua konten dipaksa jualan.",
        ],
    },
]


INDONESIAN_VAL_EXAMPLES: list[dict[str, Any]] = [
    {
        "topic": "Mengapa konten yang terlalu aman sering tidak meninggalkan kesan",
        "tone": "bold",
        "audience": "personal brands Indonesia",
        "language": "Indonesian",
        "count": 1,
        "max_chars": 210,
        "include_hashtags": False,
        "quality_criteria": COMMON_QUALITY_CRITERIA + [
            "Berani, tapi tetap profesional.",
            "Ada opini yang jelas.",
        ],
        "avoid": [
            "Terlalu provokatif tanpa isi.",
            "Clickbait kosong.",
        ],
        "reference_posts": [
            "Konten yang terlalu aman biasanya mudah disetujui, tapi cepat dilupakan. Kalau kamu ingin diingat, harus ada sudut pandang yang jelas. Bukan asal kontroversial, tapi berani punya posisi."
        ],
    },
    {
        "topic": "Cara mengubah insight meeting internal jadi konten yang relevan untuk audiens luar",
        "tone": "insightful",
        "audience": "content strategists Indonesia",
        "language": "Indonesian",
        "count": 2,
        "max_chars": 240,
        "include_hashtags": False,
        "quality_criteria": COMMON_QUALITY_CRITERIA + [
            "Jelaskan cara menerjemahkan insight internal ke konteks publik.",
            "Tidak membocorkan informasi sensitif.",
        ],
        "avoid": [
            "Menyebut data internal rahasia.",
            "Bahasa terlalu korporat.",
        ],
        "reference_posts": [
            "Insight meeting internal bisa jadi konten kalau kamu ubah dari “apa yang terjadi di tim” menjadi “apa pelajaran yang relevan untuk audiens”. Buang detail sensitif, ambil pola pikirnya.",
            "Tidak semua hasil meeting layak diposting. Tapi keputusan, trade-off, dan pertanyaan yang muncul sering bisa jadi konten bagus kalau dibingkai sebagai pembelajaran umum.",
        ],
    },
    {
        "topic": "Mengapa konten yang jujur soal proses sering lebih dipercaya daripada hasil akhir saja",
        "tone": "honest",
        "audience": "builders Indonesia",
        "language": "Indonesian",
        "count": 1,
        "max_chars": 220,
        "include_hashtags": False,
        "quality_criteria": COMMON_QUALITY_CRITERIA + [
            "Tunjukkan nilai transparansi proses.",
            "Tidak terdengar seperti curhat berlebihan.",
        ],
        "avoid": [
            "Oversharing personal.",
            "Motivasi kosong.",
        ],
        "reference_posts": [
            "Hasil akhir menunjukkan kamu berhasil. Proses menunjukkan kamu berpikir. Itu sebabnya konten yang jujur soal trial, error, dan keputusan sulit sering terasa lebih dipercaya daripada sekadar pamer pencapaian."
        ],
    },
    {
        "topic": "Cara menjelaskan trade-off produk ke audiens tanpa terdengar defensif",
        "tone": "professional",
        "audience": "product teams Indonesia",
        "language": "Indonesian",
        "count": 2,
        "max_chars": 230,
        "include_hashtags": False,
        "quality_criteria": COMMON_QUALITY_CRITERIA + [
            "Jelaskan trade-off dengan jujur dan tenang.",
            "Tunjukkan bahwa keputusan produk bisa dikomunikasikan tanpa meminta maaf berlebihan.",
        ],
        "avoid": [
            "Nada defensif.",
            "Bahasa terlalu teknis atau internal.",
        ],
        "reference_posts": [
            "Trade-off produk tidak harus dijelaskan seperti pembelaan diri. Jelaskan pilihan yang diambil, kenapa itu masuk akal untuk mayoritas user, dan apa konsekuensinya. Jelas lebih baik daripada berputar-putar.",
            "Audiens biasanya lebih bisa menerima keputusan yang tidak sempurna kalau kamu jujur soal prioritasnya. Yang bikin defensif terasa buruk bukan keputusan sulitnya, tapi cara menjelaskannya yang kabur.",
        ],
    },
    {
        "topic": "Mengapa konten edukasi perlu punya contoh, bukan hanya definisi",
        "tone": "educational",
        "audience": "educational creators Indonesia",
        "language": "Indonesian",
        "count": 1,
        "max_chars": 220,
        "include_hashtags": True,
        "quality_criteria": COMMON_QUALITY_CRITERIA + [
            "Tekankan pentingnya contoh konkret.",
            "Hashtag maksimal 2.",
        ],
        "avoid": [
            "Penjelasan terlalu akademis.",
            "Hashtag berlebihan.",
        ],
        "reference_posts": [
            "Definisi membuat orang tahu. Contoh membuat orang paham. Kalau bikin konten edukasi, jangan berhenti di “apa itu”. Tunjukkan situasi nyata supaya audiens bisa langsung mengaitkan. #ContentEducation"
        ],
    },
]


def build_indonesian_gepa_trainset() -> list[dict[str, Any]]:
    """
    Use this if your pipeline still consumes plain dict examples.
    Extra fields like quality_criteria, avoid, and reference_posts can be used
    by your metric / evaluator to give better GEPA feedback.
    """
    return INDONESIAN_TRAIN_EXAMPLES


def build_indonesian_gepa_valset() -> list[dict[str, Any]]:
    """
    Validation examples should test generalization.
    Keep them related to Indonesian social content, but not too similar
    to the train examples.
    """
    return INDONESIAN_VAL_EXAMPLES
