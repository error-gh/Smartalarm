import streamlit as st
import datetime
import time
import random

st.set_page_config(page_title="Smart Math & Task Alarm", page_icon="🚨", layout="centered")

st.title("BrainAwake Alarm")
st.write("Aplikasi alarm anti-tidur dengan tantangan Matematika & TypeRacer!")

# Inisialisasi State
if "state" not in st.session_state:
    st.session_state.state = "IDLE"  # Pilihannya: IDLE, WAITING, ALARMING
if "target_alarm_seconds" not in st.session_state:
    st.session_state.target_alarm_seconds = 0
if "stage" not in st.session_state:
    st.session_state.stage = 0
if "target_stages" not in st.session_state:
    st.session_state.target_stages = 3
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

# Ambil waktu WIB saat ini (UTC + 7 jam)
utc_now = datetime.datetime.now(datetime.timezone.utc)
wib_now = utc_now + datetime.timedelta(hours=7)
current_time_obj = wib_now.time()
current_seconds = current_time_obj.hour * 3600 + current_time_obj.minute * 60 + current_time_obj.second

# --- KONDISI 1: IDLE (PILIH WAKTU & SETEL ALARM) ---
if st.session_state.state == "IDLE":
    st.subheader("⏰ Pengaturan Alarm (WIB / UTC+7)")
    st.write(f"Waktu server WIB saat ini: **{current_time_obj.strftime('%H:%M:%S')}**")
    
    with st.form("alarm_form"):
        alarm_time = st.time_input("Pilih Waktu Alarm Berbunyi", datetime.time(current_time_obj.hour, current_time_obj.minute + 1))
        submitted = st.form_submit_button("Aktifkan Alarm", type="primary")
        
        if submitted:
            alarm_seconds = alarm_time.hour * 3600 + alarm_time.minute * 60
            st.session_state.target_alarm_seconds = alarm_seconds
            st.session_state.state = "WAITING"
            st.rerun()

# --- KONDISI 2: WAITING (MENUNGGU WAKTU ALARM TIBA) ---
elif st.session_state.state == "WAITING":
    target_sec = st.session_state.target_alarm_seconds
    target_hr = target_sec // 3600
    target_min = (target_sec % 3600) // 60
    
    st.info(f"⏳ Alarm aktif disetel pada jam **{target_hr:02d}:{target_min:02d} WIB**. Jangan tutup halaman ini!")
    st.write(f"Jam WIB server saat ini: `{current_time_obj.strftime('%H:%M:%S')}`")
    
    if st.button("❌ Batalkan / Reset Alarm"):
        st.session_state.state = "IDLE"
        st.rerun()
        
    # Cek apakah waktu sekarang sudah mencapai atau melewati target
    if current_seconds >= target_sec:
        st.session_state.state = "ALARMING"
        st.rerun()
    else:
        # Refresh otomatis halaman setiap 5 detik untuk memantau waktu
        time.sleep(5)
        st.rerun()

# --- KONDISI 3: ALARMING (ALARM BERBUNYI & TANTANGAN DIMULAI) ---
elif st.session_state.state == "ALARMING":
    st.error("🚨 WAKTU TIBA! ALARM BERBUNYI! Selesaikan tantangan untuk mematikan alarm!")
    
    st.markdown("""
        <audio autoplay loop>
          <source src="https://assets.mixkit.co/active_storage/sfx/1005/1005-preview.mp3" type="audio/mpeg">
        </audio>
    """, unsafe_allow_html=True)
    
    st.write(f"### Progres Tahapan Berhasil: {st.session_state.stage} / {st.session_state.target_stages}")
    
    if st.session_state.current_challenge is None:
        st.session_state.current_challenge = random.choice(['math', 'typeracer'])
        if st.session_state.current_challenge == 'math':
            q, a = generate_math()
            st.session_state.q_text = q
            st.session_state.ans_correct = a
        else:
            s = random.choice(sentences)
            st.session_state.target_sentence = s

    if st.session_state.current_challenge == 'math':
        st.write(f"**🧮 Tantangan Matematika:**")
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
                    st.error("❌ Salah! Progres direset ke 0.")
                    st.session_state.stage = 0
                    st.session_state.current_challenge = None
                    st.rerun()
            except ValueError:
                st.warning("⚠️ Masukkan angka yang valid!")

    else:
        st.write(f"**⌨️ Tantangan TypeRacer:**")
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
                st.error("❌ Ketikan tidak sesuai! Progres direset ke 0.")
                st.session_state.stage = 0
                st.session_state.current_challenge = None
                st.rerun()
