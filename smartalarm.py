import streamlit as st
import datetime
import time
import random

st.set_page_config(page_title="Smart Math & Task Alarm", page_icon="🚨", layout="centered")

st.title("BrainAwake Alarm")
st.write("Aplikasi alarm anti-tidur dengan tantangan interaktif!")

# Inisialisasi Session State
if "state" not in st.session_state:
    st.session_state.state = "IDLE"  # Status: IDLE, WAITING, ALARMING
if "target_alarm_seconds" not in st.session_state:
    st.session_state.target_alarm_seconds = 0
if "stage" not in st.session_state:
    st.session_state.stage = 0
if "target_stages" not in st.session_state:
    st.session_state.target_stages = 3
if "allowed_modes" not in st.session_state:
    st.session_state.allowed_modes = ["math", "typeracer"]
if "current_challenge" not in st.session_state:
    st.session_state.current_challenge = None

# Modul Soal Matematika
def generate_math():
    operator = random.choice(['+', '-', '*', '/'])
    if operator == '+':
        n1, n2 = random.randint(1, 50), random.randint(1, 50)
        ans = n1 + n2
    elif operator == '-':
        n1, n2 = random.randint(1, 50), random.randint(1, 50)
        if n1 < n2: n1, n2 = n2, n1
        ans = n1 - n2
    elif operator == '*':
        n1, n2 = random.randint(2, 12), random.randint(2, 12)
        ans = n1 * n2
    else:
        n2 = random.randint(2, 10)
        mult = random.randint(2, 10)
        n1 = n2 * mult
        ans = mult
    return f"Berapa hasil dari {n1} {operator} {n2}?", ans

# Daftar Kalimat TypeRacer
sentences = [
    "Bangun pagi adalah kunci utama kesuksesan hari ini",
    "Jangan biarkan rasa malas mengalahkan impian besarmu",
    "Koding setiap hari membuat otak semakin tajam dan kreatif",
    "Semangat belajar informatika untuk masa depan yang cerah",
    "Konsistensi adalah rahasia dibalik hasil yang luar biasa",
    "Sukses tidak datang bagi mereka yang hanya tidur, tapi bagi yang berusaha",
    "Fokus pada proses dan nikmati setiap tantangan yang ada",
    "Matematika dan pemrograman adalah kombinasi logika yang sempurna",
    "Hari baru kesempatan baru untuk menjadi versi terbaik dirimu",
    "Aplikasi hebat dibuat dari baris-baris kode yang ditulis dengan teliti"
]

# Waktu server saat ini (WIB / UTC+7)
utc_now = datetime.datetime.now(datetime.timezone.utc)
wib_now = utc_now + datetime.timedelta(hours=7)
current_time_obj = wib_now.time()
current_seconds = current_time_obj.hour * 3600 + current_time_obj.minute * 60 + current_time_obj.second

# --- KONDISI 1: IDLE (PENGATURAN ALARM & TANTANGAN) ---
if st.session_state.state == "IDLE":
    st.subheader("⏰ Pengaturan Alarm & Modus Tantangan")
    st.write(f"Waktu server WIB saat ini: **{current_time_obj.strftime('%H:%M:%S')}**")
    
    with st.form("alarm_form"):
        alarm_time = st.time_input("Pilih Waktu Alarm Berbunyi", datetime.time(current_time_obj.hour, (current_time_obj.minute + 1) % 60))
        
        # Pengaturan Streak / Target Tahapan
        target_streak = st.number_input("Target Streak Berhasil (Berapa kali jawab benar?):", min_value=1, max_value=10, value=3, step=1)
        
        st.write("---")
        st.write("⚙️ **Pilih Jenis Tantangan yang Ingin Digunakan:**")
        use_math = st.checkbox("🧮 Soal Matematika", value=True)
        use_typeracer = st.checkbox("⌨️ TypeRacer (Ketik Kalimat)", value=True)
        
        submitted = st.form_submit_button("Aktifkan Alarm", type="primary")
        
        if submitted:
            if not use_math and not use_typeracer:
                st.error("⚠️ Kamu harus memilih minimal satu jenis tantangan (Matematika / TypeRacer)!")
            else:
                modes = []
                if use_math: modes.append("math")
                if use_typeracer: modes.append("typeracer")
                
                st.session_state.allowed_modes = modes
                st.session_state.target_stages = target_streak
                st.session_state.target_alarm_seconds = alarm_time.hour * 3600 + alarm_time.minute * 60
                st.session_state.state = "WAITING"
                st.session_state.stage = 0
                st.rerun()

# --- KONDISI 2: WAITING (MENUNGGU WAKTU ALARM TIBA) ---
elif st.session_state.state == "WAITING":
    target_sec = st.session_state.target_alarm_seconds
    target_hr = target_sec // 3600
    target_min = (target_sec % 3600) // 60
    
    st.info(f"⏳ Alarm aktif disetel pada jam **{target_hr:02d}:{target_min:02d} WIB** (Target Streak: {st.session_state.target_stages}). Jangan tutup halaman ini!")
    st.write(f"Jam WIB server saat ini: `{current_time_obj.strftime('%H:%M:%S')}`")
    
    if st.button("❌ Batalkan / Reset Alarm"):
        st.session_state.state = "IDLE"
        st.rerun()
        
    if current_seconds >= target_sec:
        st.session_state.state = "ALARMING"
        st.rerun()
    else:
        time.sleep(5)
        st.rerun()

# --- KONDISI 3: ALARMING (ALARM BERBUNYI & TANTANGAN BERJALAN) ---
elif st.session_state.state == "ALARMING":
    st.error("🚨 WAKTU TIBA! ALARM SIRINE BERBUNYI! Selesaikan tantangan untuk mematikan alarm!")
    
    # Audio Alarm Pilihan 3: Sirine Nuklir / Evakuasi
    st.markdown("""
        <audio autoplay loop controls>
          <source src="https://assets.mixkit.co/active_storage/sfx/1005/1005-preview.mp3" type="audio/mpeg">
        </audio>
    """, unsafe_allow_html=True)
    
    st.write(f"### Progres Streak Berhasil: {st.session_state.stage} / {st.session_state.target_stages}")
    
    # Pilih tantangan berdasarkan opsi centang pengguna di awal
    if st.session_state.current_challenge is None:
        st.session_state.current_challenge = random.choice(st.session_state.allowed_modes)
        if st.session_state.current_challenge == 'math':
            q, a = generate_math()
            st.session_state.q_text = q
            st.session_state.ans_correct = a
        else:
            s = random.choice(sentences)
            st.session_state.target_sentence = s

    # Tampilan Form Soal Matematika
    if st.session_state.current_challenge == 'math':
        st.write("**🧮 Tantangan Matematika:**")
        st.write(st.session_state.q_text)
        user_ans = st.text_input("Masukkan jawaban angka:", key="math_ans")
        
        if st.button("Kirim Jawaban"):
            try:
                if int(user_ans) == st.session_state.ans_correct:
                    st.success("✅ Benar!")
                    st.session_state.stage += 1
                    st.session_state.current_challenge = None
                    if st.session_state.stage >= st.session_state.target_stages:
                        st.session_state.state = "IDLE"
                        st.session_state.stage = 0
                        st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Salah! Progres streak direset ke 0.")
                    st.session_state.stage = 0
                    st.session_state.current_challenge = None
                    st.rerun()
            except ValueError:
                st.warning("⚠️ Masukkan angka yang valid!")

    # Tampilan Form TypeRacer
    else:
        st.write("**⌨️ Tantangan TypeRacer:**")
        st.markdown(f"> `{st.session_state.target_sentence}`")
        user_typing = st.text_input("Ketik ulang kalimat di atas:", key="type_ans")
        
        if st.button("Kirim Kalimat"):
            if user_typing.strip() == st.session_state.target_sentence:
                st.success("✅ Sempurna!")
                st.session_state.stage += 1
                st.session_state.current_challenge = None
                if st.session_state.stage >= st.session_state.target_stages:
                    st.session_state.state = "IDLE"
                    st.session_state.stage = 0
                    st.balloons()
                    st.rerun()
                else:
                    st.rerun()
            else:
                st.error("❌ Ketikan tidak sesuai! Progres streak direset ke 0.")
                st.session_state.stage = 0
                st.session_state.current_challenge = None
                st.rerun()
