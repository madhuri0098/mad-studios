import asyncio
import datetime
import json
import certifi
import httpx
import edge_tts
import fal_client
from moviepy import VideoFileClip, AudioFileClip, vfx
import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
import base64

@st.cache_data
def b64_img(path):
    if not os.path.exists(path):
        return ""
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
    with open(path, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"

st.set_page_config(page_title="Mad Studios", page_icon="🐙", layout="wide")

st.markdown("""
<style>
@import url('https://googleapis.com');
.stApp { overflow-x: hidden; }

.stApp { background: url("/app/static/bg.gif") center/cover no-repeat fixed !important; overflow-x: hidden; }
header[data-testid="stHeader"], section[data-testid="stSidebar"] { display: none !important; }
.block-container { padding-top: 1.2rem !important; max-width: 1400px !important; }

/* 1. Top-Left 86px Circular Avatar + Exact Matching Hitbox */
.maddy-avatar-pin {
    position: fixed; top: 14px; left: 16px; z-index: 9998;
    width: 86px; height: 86px; border-radius: 50%; object-fit: cover;
    border: 3.5px solid #6b0f2b; box-shadow: 0 8px 20px rgba(107,15,43,0.38); pointer-events: none;
}
/* Pin the invisible 86px click trigger directly over Maddy's top-left avatar */
div[data-testid="stPopover"] {
    position: fixed !important; top: 14px !important; left: 16px !important; z-index: 9999 !important;
    width: 86px !important; height: 86px !important;
}
div[data-testid="stPopover"] button {
    width: 86px !important; height: 86px !important; min-height: 86px !important;
    border-radius: 50% !important; padding: 0 !important;
    background: transparent !important; border: none !important; color: transparent !important;
    box-shadow: none !important; cursor: pointer !important;
}
div[data-testid="stPopover"] button * { opacity: 0 !important; }

/* Keep Top-Right "Your Projects" in its normal spot & color it Burgundy */
div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] {
    position: relative !important; top: auto !important; left: auto !important;
    width: auto !important; height: auto !important;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] button {
    width: auto !important; height: auto !important; min-height: 40px !important;
    padding: 0.45rem 1rem !important;
    background: linear-gradient(135deg, #6b0f2b 0%, #8e183b 100%) !important;
    color: #fce4ec !important; border: 1.5px solid #a8244b !important;
    border-radius: 999px !important; font-weight: 700 !important;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] button * {
    opacity: 1 !important; color: #fce4ec !important; fill: #fce4ec !important;
}
/* Pastel Pink Dropdown Container & Compact Burgundy Tabs */
div[data-baseweb="popover"] > div,
div[data-testid="stPopoverBody"] {
    background: linear-gradient(180deg, #fce4ec 0%, #f8bbd0 100%) !important;
    border: 2.5px solid #6b0f2b !important;
    border-radius: 18px !important;
    padding: 0.55rem 0.7rem !important;
    max-height: 82vh !important;
    overflow-y: auto !important;
}
div[data-baseweb="popover"] hr {
    border-color: rgba(107, 15, 43, 0.25) !important;
    margin: 0.25rem 0 !important;
}
div[data-testid="stPopoverBody"] {
    --secondary-background-color: #6b0f2b !important;
    --background-color: #6b0f2b !important;
    --text-color: #fce4ec !important;
}
div[data-testid="stPopoverBody"] button {
    background-color: #6b0f2b !important;
    background-image: linear-gradient(135deg, #6b0f2b 0%, #8e183b 100%) !important;
    color: #fce4ec !important;
    border: 1.5px solid #a8244b !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
}
div[data-testid="stPopoverBody"] button p {
    color: #fce4ec !important;
}
div[data-testid="stPopoverBody"] button:hover {
    background-color: #4a081d !important;
    background-image: none !important;
}

/* 4. Cursive Title, Baby Pink Speech Bubble & Feathered Sea Animals */
.mad-title { font-family: 'Pacifico', cursive; font-size: 3.1rem; color: #6b0f2b; text-align: center; text-shadow: 0 3px 10px rgba(255,255,255,0.85); }
.mad-sub { text-align: center; color: #6b0f2b; font-weight: 800; font-size: 1.15rem; margin-top: -8px; }
.speech-bubble {
    background: linear-gradient(135deg, #ffd6e7 0%, #ffc2dc 100%) !important;
    border: 2px solid #8e183b !important; border-radius: 26px !important; padding: 0.95rem 1.2rem !important;
    color: #6b0f2b !important; font-weight: 800 !important; text-align: center; margin-top: 1.8rem;
}
.blended-sea, .hero-octo {
    border-radius: 50%;
    -webkit-mask-image: radial-gradient(circle, rgba(0,0,0,1) 42%, rgba(0,0,0,0) 70%);
    mask-image: radial-gradient(circle, rgba(0,0,0,1) 42%, rgba(0,0,0,0) 70%);
}
.blended-sea { position: fixed; pointer-events: none; z-index: 1; }
.hero-octo { width: 195px; }

/* 5. Pastel Pink Search Bar & Burgundy Typed Font */
div[data-testid="stChatInput"] > div { border: 2.5px solid #6b0f2b !important; border-radius: 999px !important; background: #fce4ec !important; }
div[data-testid="stChatInput"] textarea { color: #6b0f2b !important; font-weight: 700 !important; background: transparent !important; }
div[data-testid="stChatInput"] textarea::placeholder { color: #8e183b !important; opacity: 0.8 !important; }
button[data-testid="stChatInputSubmitButton"] { background: #6b0f2b !important; border-radius: 50% !important; }
button[data-testid="stChatInputSubmitButton"] svg { fill: #fce4ec !important; }
</style>
""", unsafe_allow_html=True)
st.markdown(f"""
<style>
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
    background: url("{b64_img('static/bg.gif')}") center/cover no-repeat fixed !important;
}}
</style>
""", unsafe_allow_html=True)

if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "HOME"

# Top-Left Clickable Avatar Menu
av_src = b64_img("static/custom_maddy.png") if os.path.exists("static/custom_maddy.png") else b64_img("static/maddy.jpg")
st.markdown(f'<img src="{av_src}" class="maddy-avatar-pin">', unsafe_allow_html=True)
with st.popover(" "):
    if st.button("HOME", use_container_width=True):
        st.session_state["active_tab"] = "HOME"
        st.rerun()
    st.markdown("---")
    for t in ["PROFILE", "TEXT-TO-REEL", "TEXT-TO-IMAGE", "VIDEO-TO-TEXT", "TEXT-TO-AUDIO", "ABOUT US", "WHY CHOOSE US"]:
        if t == "ABOUT US":
            st.markdown("---")
        if st.button(t, use_container_width=True):
            st.session_state["active_tab"] = t
            st.rerun()

# Top-Right Burgundy Your Projects
_, top_r = st.columns([4.2, 1.0])
with top_r:
     with st.popover("📁 Your Projects"):
        st.markdown("### Your Work")
        os.makedirs("finished_reels", exist_ok=True)
        os.makedirs("finished_images", exist_ok=True)

        reels = [(f, os.path.join("finished_reels", f)) for f in sorted(os.listdir("finished_reels"), reverse=True) if f.endswith(".mp4")]
        imgs = [(f, os.path.join("finished_images", f)) for f in sorted(os.listdir("finished_images"), reverse=True) if f.endswith((".png", ".jpg", ".jpeg"))]
        all_work = reels + imgs

        if all_work:
            st.caption("Click any file to open in full view:")
            for idx, (fname, fpath) in enumerate(all_work):
                icon = "🎬" if fname.endswith(".mp4") else "🎨"
                if st.button(f"{icon} {fname}", key=f"work_btn_{idx}", use_container_width=True):
                    st.session_state["selected_work"] = fpath
                    st.session_state["active_tab"] = "YOUR WORK"
                    st.rerun()
        else:
            st.write("No saved work yet!")

active = st.session_state["active_tab"]

if active == "HOME":
    st.markdown(f"""
    <img src="{b64_img('static/seahorse.gif')}" class="blended-sea" style="top:34%; left:2%; width:115px;">
    <img src="{b64_img('static/dolphin.gif')}"  class="blended-sea" style="top:22%; left:10%; width:175px;">
    <img src="{b64_img('static/ray.gif')}"      class="blended-sea" style="top:15%; left:26%; width:135px;">
    <img src="{b64_img('static/crab.gif')}"     class="blended-sea" style="bottom:3%; left:4%; width:160px;">
    <img src="{b64_img('static/turtle.gif')}"   class="blended-sea" style="top:20%; right:18%; width:160px;">
    <img src="{b64_img('static/clam.gif')}"     class="blended-sea" style="bottom:3%; right:14%; width:140px;">
    """, unsafe_allow_html=True)
   
    _, hero_col, _ = st.columns([0.85, 2.3, 0.85])
    with hero_col:
        st.markdown('<div class="mad-title">Mad Studios</div><div class="mad-sub">• Instant AI Bot •</div>', unsafe_allow_html=True)
        b_col, octo_col, _ = st.columns([1.25, 1.15, 0.7])
        with b_col:
            st.markdown('<div class="speech-bubble">Hi! I\'m Maddy\'s Octopus Bot 🐙<br>How can I help you create today?</div>', unsafe_allow_html=True)
        with octo_col:
            st.markdown(f'<img src="{b64_img("static/octopus.gif")}" class="hero-octo">', unsafe_allow_html=True)


        if "chat_msgs" not in st.session_state:
            st.session_state["chat_msgs"] = []
        for m in st.session_state["chat_msgs"]:
            with st.chat_message(m["role"], avatar="🐙" if m["role"] == "assistant" else "🎀"):
                st.write(m["content"])

        if prompt := st.chat_input("Ask Maddy's Octopus Bot anything..."):
            st.session_state["chat_msgs"].append({"role": "user", "content": prompt})
            res = Groq(api_key=os.getenv("GROQ_KEY")).chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role": "system", "content": "You are Maddy's cute Octopus Bot inside Mad Studios."}] + st.session_state["chat_msgs"]
            )
            st.session_state["chat_msgs"].append({"role": "assistant", "content": res.choices.message.content})
            st.rerun()

else:
    _, work_col, _ = st.columns([0.55, 2.9, 0.55])
    with work_col:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #6b0f2b 0%, #8e183b 50%, #520920 100%);
            border: 2px solid #f48fb1; border-radius: 999px;
            padding: 0.7rem 1.5rem; margin-bottom: 1.2rem;
            display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 8px 20px rgba(107,15,43,0.28);
            color: #fce4ec; font-weight: 800;
        ">
            <span>⭐ 🐚 ✨</span>
            <span>{active}</span>
            <span>✨ 🐚 ⭐</span>
        </div>
        """, unsafe_allow_html=True)

        if active == "TEXT-TO-REEL":
            REEL_VOICES = {
                "✨ ElevenLabs • Chutki Style (Young, Cute & Playful)": ("elevenlabs", "chutki"),
                "🎀 Chutki Style • Indian English (Bubbly Cartoon)": ("en-IN-KavyaNeural", "+55Hz"),
                "🎀 Chutki Style • Hindi (Bubbly Cartoon)": ("hi-IN-SwaraNeural", "+55Hz"),
                "🇮🇳 Neerja • Indian English (Cute Kid)": ("en-IN-NeerjaNeural", "+48Hz"),
                "🇮🇳 Kavya • Indian English (Playful Kid)": ("en-IN-KavyaNeural", "+48Hz"),
                "🇮🇳 Swara • Hindi (Cute Kid)": ("hi-IN-SwaraNeural", "+48Hz"),
                "🇺🇸 Ana • US English (Cute Kid)": ("en-US-AnaNeural", "+15Hz"),
                "🇰🇷 SunHi • Korean (Sweet Anime)": ("ko-KR-SunHiNeural", "+30Hz"),
            }


            c_s1, c_s2 = st.columns([2.2, 1])
            with c_s2:
                st.write("")
                if st.button("✨ AI Write Scene & Script", use_container_width=True):
                    hint = st.session_state.get("t2r_scene", "") or "Maddy eating spicy Maggi at 2 AM with fairy lights"
                    with st.spinner("Writing scene & dialogue..."):
                        res = Groq(api_key=os.getenv("GROQ_KEY")).chat.completions.create(
                            model="openai/gpt-oss-20b",
                            messages=[
                                {"role": "system", "content": "Return valid JSON with keys 'scene' (visual description of chibi Indian girl Maddy facing camera) and 'dialogue' (cute 18-word spoken script)."},
                                {"role": "user", "content": hint}
                            ],
                            response_format={"type": "json_object"}
                        )
                        data = json.loads(res.choices[0].message.content)
                        st.session_state["t2r_scene"] = data["scene"]
                        st.session_state["t2r_dialogue"] = data["dialogue"]

            with c_s1:
                st.text_area("1️⃣ Scene Description:", key="t2r_scene", height=80, placeholder="Describe where Maddy is and what she is doing...")

            aud_mode = st.radio("2️⃣ Audio Option:", ["🗣️ Maddy AI Voice", "📁 Upload Audio (.mp3/.wav)"], horizontal=True)
            up_aud_path = None
            sel_voice = list(REEL_VOICES.keys())

            async def make_tts(text, vid, pitch, out_mp3, custom_el_id=""):
                clean = "".join(c for c in text if ord(c) < 0x10000).strip() or "Hi everyone!"
                if vid == "elevenlabs":
                    os.environ["FAL_KEY"] = os.getenv("FAL_KEY") or ""
                    voice_target = custom_el_id.strip() if custom_el_id.strip() else "Alice"
                    res = fal_client.subscribe(
                        "fal-ai/elevenlabs/tts/multilingual-v2",
                        arguments={
                            "text": clean,
                            "voice": voice_target,
                            "stability": 0.42,
                            "similarity_boost": 0.80,
                            "style": 0.45
                        }
                    )
                    with httpx.Client(verify=certifi.where(), follow_redirects=True, timeout=60.0) as c:
                        open(out_mp3, "wb").write(c.get(res["audio"]["url"]).content)
                else:
                    from gtts import gTTS
                    lang = "hi" if vid.startswith("hi-") else "en"
                    tld = "co.in" if "-IN-" in vid else "com"
                    gTTS(text=clean, lang=lang, tld=tld).save(out_mp3)

            custom_el_id = ""
            if aud_mode == "🗣️ Maddy AI Voice":
                sel_voice = st.selectbox("Select Voice:", list(REEL_VOICES.keys()))
                if sel_voice.startswith("✨ ElevenLabs"):
                    custom_el_id = st.text_input(
                        "Optional: Paste exact ElevenLabs Voice ID (leave blank for built-in cute playful voice):",
                        placeholder="e.g. 21m00Tcm4TlvDq8ikWAM"
                    )
                st.text_area("Maddy's Spoken Dialogue:", key="t2r_dialogue", height=80, placeholder="Hiii everyone! Welcome to my channel!")
                if st.button("🔊 Preview Voice"):
                    if st.session_state.get("t2r_dialogue", "").strip():
                        vid, pitch = REEL_VOICES[sel_voice]
                        asyncio.run(make_tts(st.session_state["t2r_dialogue"], vid, pitch, "preview_reel.mp3", custom_el_id))
                        st.audio("preview_reel.mp3")

            else:
                uf = st.file_uploader("Upload Audio File", type=["mp3", "wav", "m4a"])
                if uf:
                    up_aud_path = "uploaded_reel_aud.mp3"
                    open(up_aud_path, "wb").write(uf.getbuffer())
                    st.audio(up_aud_path)

            if st.button("🚀 Generate Complete 9:16 Reel", type="primary", use_container_width=True):
                if not st.session_state.get("t2r_scene", "").strip():
                    st.warning("Please enter or generate a Scene first!")
                elif aud_mode == "🗣️ Maddy AI Voice" and not st.session_state.get("t2r_dialogue", "").strip():
                    st.warning("Please write Maddy's dialogue first!")
                elif aud_mode == "📁 Upload Audio (.mp3/.wav)" and not up_aud_path:
                    st.warning("Please upload an audio file first!")
                else:
                    os.makedirs("finished_reels", exist_ok=True)
                    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    out_mp4 = f"finished_reels/Maddy_Reel_{ts}.mp4"
                    with st.status("🎬 Producing your 9:16 Animated Reel...", expanded=True) as status:
                        if aud_mode == "🗣️ Maddy AI Voice":
                            st.write("🎙️ Generating Maddy's natural voice...")
                            vid, pitch = REEL_VOICES[sel_voice]
                            asyncio.run(make_tts(st.session_state["t2r_dialogue"], vid, pitch, "reel_voice.mp3", custom_el_id))
                            aud_final = "reel_voice.mp3"
                        else:
                            aud_final = up_aud_path

                        st.write("🎨 Step 1/3: Rendering 3D Pixar-style character frame...")
                        os.environ["FAL_KEY"] = os.getenv("FAL_KEY") or ""
                        up_maddy = fal_client.upload_file("maddy.jpg")
                        img_res = fal_client.subscribe(
                            "fal-ai/flux-pro/kontext",
                            arguments={
                                "prompt": (
                                    "3D Pixar and Disney animated movie style, keeping this exact cute Indian chibi girl "
                                    "with her tiny red bindi, dark wavy hair, and outfit, rich cinematic lighting, "
                                    "soft depth of field, expressive animated eyes and lively pose: "
                                    f"{st.session_state['t2r_scene']}"
                                ),
                                "image_url": up_maddy,
                                "aspect_ratio": "9:16"
                            }
                        )
                        with httpx.Client(verify=certifi.where(), follow_redirects=True, timeout=120.0) as c:
                            open("reel_frame.png", "wb").write(c.get(img_res["images"][0]["url"]).content)

                        
                        with httpx.Client(verify=certifi.where(), follow_redirects=True, timeout=180.0) as c:
                            open("reel_motion.mp4", "wb").write(c.get(vid_res["video"]["url"]).content)

                            sync_res = fal_client.subscribe("fal-ai/kling-video/lipsync/audio-to-video", arguments={"video_url": fal_client.upload_file("reel_motion.mp4"), "audio_url": fal_client.upload_file(aud_final)})

                            arguments={
                                "video_url": fal_client.upload_file("reel_motion.mp4"),
                                "audio_url": fal_client.upload_file(aud_final)
                            }
                        
                        with httpx.Client(verify=certifi.where(), follow_redirects=True, timeout=180.0) as c:
                            open(out_mp4, "wb").write(c.get(sync_res["video"]["url"]).content)

                        status.update(label="🎉 Your 9:16 Animated Reel is ready!", state="complete", expanded=False)

                    if "session_reels" not in st.session_state:
                        st.session_state["session_reels"] = []
                    st.session_state["session_reels"].insert(0, out_mp4)

            if st.session_state.get("session_reels"):
                st.markdown("---")
                st.subheader("🎞️ Your Reels (Current Session)")
                st.caption("These reels stay here while this session is open and are permanently saved in 📁 Your Projects.")
                for idx, r_path in enumerate(st.session_state["session_reels"]):
                    if os.path.exists(r_path):
                        st.video(r_path)
                        with open(r_path, "rb") as f:
                            st.download_button(
                                f"⬇️ Download {os.path.basename(r_path)}",
                                data=f,
                                file_name=os.path.basename(r_path),
                                mime="video/mp4",
                                key=f"dl_sess_{idx}",
                                use_container_width=True)
                       # =========================================================
        # TAB: PROFILE (YOUR PROFILE, NAME, EMAIL & AVATAR)
        # =========================================================
        elif active == "PROFILE":
            st.subheader("Your Profile")

            # Load saved profile details if available
            prof_data = {"name": "", "email": ""}
            if os.path.exists("profile.json"):
                try:
                    prof_data = json.load(open("profile.json", "r", encoding="utf-8"))
                except Exception:
                    pass

            p_col1, p_col2 = st.columns([1, 1.8])
            with p_col1:
                cur_av = "static/custom_maddy.png" if os.path.exists("static/custom_maddy.png") else "static/maddy.jpg"
                if os.path.exists(cur_av):
                    st.image(cur_av, caption="Current Avatar", width=220)

            with p_col2:
                n_col, e_col = st.columns(2)
                with n_col:
                    u_name = st.text_input("Name:", value=prof_data.get("name", ""), placeholder="Enter your name")
                with e_col:
                    u_email = st.text_input("Email:", value=prof_data.get("email", ""), placeholder="Enter your email")

                if st.button("💾 Save Profile Details", type="primary"):
                    json.dump({"name": u_name.strip(), "email": u_email.strip()}, open("profile.json", "w", encoding="utf-8"))
                    st.success("Profile details saved!")

                st.markdown("---")
                st.write("Upload your new avatar:")
                new_av = st.file_uploader("Choose Avatar Image (.png / .jpg)", type=["png", "jpg", "jpeg"], key="prof_up")
                if new_av and st.button("💾 Save as New Avatar", type="primary"):
                    os.makedirs("static", exist_ok=True)
                    with open("static/custom_maddy.png", "wb") as f:
                        f.write(new_av.getbuffer())
                    st.success("Avatar updated!")
                    st.rerun()

                if os.path.exists("static/custom_maddy.png"):
                    if st.button("🔄 Reset to Original Avatar"):
                        os.remove("static/custom_maddy.png")
                        st.rerun()


        # =========================================================
        # TAB: TEXT-TO-IMAGE (3D PIXAR MADDY IMAGE STUDIO)
        # =========================================================
        elif active == "TEXT-TO-IMAGE":
            st.subheader("🎨 Text to Image • 3D Pixar Character Studio")
            i_c1, i_c2 = st.columns([2.2, 1])
            with i_c2:
                st.write("")
                if st.button("✨ AI Enhance Prompt", use_container_width=True):
                    base_p = st.session_state.get("t2i_prompt", "") or "Maddy wearing a pastel pink lehenga holding sparklers on Diwali"
                    with st.spinner("Enhancing prompt..."):
                        res = Groq(api_key=os.getenv("GROQ_KEY")).chat.completions.create(
                            model="openai/gpt-oss-20b",
                            messages=[
                                {"role": "system", "content": "Expand the user's idea into one rich 35-word 3D Pixar animated movie scene description featuring cute Indian chibi girl Maddy with her tiny red bindi and dark wavy hair."},
                                {"role": "user", "content": base_p}
                            ]
                        )
                        st.session_state["t2i_prompt"] = res.choices[0].message.content.strip()

            with i_c1:
                st.text_area("Describe Maddy's Outfit, Pose, or Scene:", key="t2i_prompt", height=85, placeholder="e.g. Maddy wearing cute pink headphones in a neon gaming room...")

            aspect = st.radio("Aspect Ratio:", ["9:16", "1:1", "16:9"], horizontal=True)

            if st.button("🎨 Generate 3D Pixar Image", type="primary", use_container_width=True):
                if not st.session_state.get("t2i_prompt", "").strip():
                    st.warning("Please enter or enhance an image prompt first!")
                else:
                    os.makedirs("finished_images", exist_ok=True)
                    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    out_png = f"finished_images/Maddy_Img_{ts}.png"
                    with st.spinner("🎨 Rendering 3D Pixar image..."):
                        os.environ["FAL_KEY"] = os.getenv("FAL_KEY") or ""
                        up_maddy = fal_client.upload_file("maddy.jpg")
                        img_res = fal_client.subscribe(
                            "fal-ai/flux-pro/kontext",
                            arguments={
                                "prompt": (
                                    "3D Pixar and Disney animated movie style, keeping this exact cute Indian chibi girl "
                                    "with her tiny red bindi and dark wavy hair, rich cinematic lighting, soft depth of field: "
                                    f"{st.session_state['t2i_prompt']}"
                                ),
                                "image_url": up_maddy,
                                "aspect_ratio": aspect
                            }
                        )
                        with httpx.Client(verify=certifi.where(), follow_redirects=True, timeout=120.0) as c:
                            open(out_png, "wb").write(c.get(img_res["images"][0]["url"]).content)
                        st.session_state["last_t2i_img"] = out_png

            if st.session_state.get("last_t2i_img") and os.path.exists(st.session_state["last_t2i_img"]):
                img_file = st.session_state["last_t2i_img"]
                st.image(img_file, caption="Generated 3D Pixar Maddy", width=360)
                b1, b2 = st.columns(2)
                with b1:
                    with open(img_file, "rb") as f:
                        st.download_button("⬇️ Download PNG", data=f, file_name=os.path.basename(img_file), mime="image/png", use_container_width=True)
                with b2:
                    if st.button("🌟 Set as Top-Left Avatar", use_container_width=True):
                        import shutil
                        os.makedirs("static", exist_ok=True)
                        shutil.copy(img_file, "static/custom_maddy.png")
                        st.success("Updated top-left avatar!")
                        st.rerun()

                # =========================================================
        # TAB: VIDEO-TO-TEXT (100% FREE GROQ WHISPER TRANSCRIPTION)
        # =========================================================
        elif active == "VIDEO-TO-TEXT":
            st.subheader("📝 Video to Text • Fast AI Transcriber & Caption Maker")
            v_file = st.file_uploader("Upload Video or Audio (.mp4, .mov, .mp3, .wav, .m4a):", type=["mp4", "mov", "mp3", "wav", "m4a"], key="v2t_up")
            if v_file and st.button("✨ Transcribe Video / Audio", type="primary", use_container_width=True):
                with st.spinner("Transcribing with Groq Whisper..."):
                    ext = os.path.splitext(v_file.name)[1] or ".mp4"
                    tmp_media = f"temp_v2t{ext}"
                    open(tmp_media, "wb").write(v_file.getbuffer())
                    client = Groq(api_key=os.getenv("GROQ_KEY"))
                    with open(tmp_media, "rb") as af:
                        tr = client.audio.transcriptions.create(file=(tmp_media, af.read()), model="whisper-large-v3-turbo", response_format="text")
                    st.session_state["v2t_result"] = tr

            if st.session_state.get("v2t_result"):
                st.text_area("Extracted Transcript:", value=st.session_state["v2t_result"], height=160)
                c_v1, c_v2 = st.columns(2)
                with c_v1:
                    st.download_button("⬇️ Download Transcript (.txt)", data=st.session_state["v2t_result"], file_name="maddy_transcript.txt", mime="text/plain", use_container_width=True)
                with c_v2:
                    if st.button("🔥 Generate Viral Reel Caption & Hashtags", use_container_width=True):
                        with st.spinner("Writing viral caption..."):
                            cap_res = Groq(api_key=os.getenv("GROQ_KEY")).chat.completions.create(
                                model="openai/gpt-oss-20b",
                                messages=[
                                    {"role": "system", "content": "Write a catchy YouTube Shorts / Instagram Reels title, 2-line hook caption, and 8 trending hashtags based on this transcript."},
                                    {"role": "user", "content": st.session_state["v2t_result"]}
                                ]
                            )
                            st.session_state["v2t_caption"] = cap_res.choices[0].message.content
                if st.session_state.get("v2t_caption"):
                    st.info(st.session_state["v2t_caption"])

        # =========================================================
        # TAB: TEXT-TO-AUDIO (STANDALONE VOICEOVER STUDIO)
        # =========================================================
        elif active == "TEXT-TO-AUDIO":
            st.subheader("🎙️ Text to Audio • Maddy Voiceover Studio")
            TTS_VOICES = {
                "✨ ElevenLabs • Chutki Style (Young, Cute & Playful)": ("elevenlabs", "chutki"),
                "🇮🇳 Neerja • Indian English (Free)": ("en-IN-NeerjaNeural", "+48Hz"),
                "🇮🇳 Swara • Hindi (Free)": ("hi-IN-SwaraNeural", "+48Hz"),
            }
            t2a_voice = st.selectbox("Select Voice:", list(TTS_VOICES.keys()), key="t2a_sel")
            t2a_el_id = ""
            if t2a_voice.startswith("✨ ElevenLabs"):
                t2a_el_id = st.text_input("Optional: Paste exact ElevenLabs Voice ID (leave blank for built-in cute playful voice):", placeholder="e.g. 21m00Tcm4TlvDq8ikWAM", key="t2a_el")

            t2a_text = st.text_area("Enter Script to Convert into Speech:", height=110, placeholder="Hiii guys! Welcome back to Mad Studios!", key="t2a_txt")
            if st.button("🔊 Generate Audio (.mp3)", type="primary", use_container_width=True):
                if not t2a_text.strip():
                    st.warning("Please enter some text first!")
                else:
                    with st.spinner("Generating voiceover..."):
                        os.makedirs("finished_audio", exist_ok=True)
                        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        out_mp3 = f"finished_audio/Maddy_Voice_{ts}.mp3"
                        vid, _ = TTS_VOICES[t2a_voice]
                        clean = "".join(c for c in t2a_text if ord(c) < 0x10000).strip()
                        if vid == "elevenlabs":
                            os.environ["FAL_KEY"] = os.getenv("FAL_KEY") or ""
                            v_target = t2a_el_id.strip() if t2a_el_id.strip() else "Alice"
                            res = fal_client.subscribe("fal-ai/elevenlabs/tts/multilingual-v2", arguments={"text": clean, "voice": v_target, "stability": 0.42, "similarity_boost": 0.80, "style": 0.45})
                            with httpx.Client(verify=certifi.where(), follow_redirects=True, timeout=60.0) as c:
                                open(out_mp3, "wb").write(c.get(res["audio"]["url"]).content)
                        else:
                            from gtts import gTTS
                            lang = "hi" if vid.startswith("hi-") else "en"
                            tld = "co.in" if "-IN-" in vid else "com"
                            gTTS(text=clean, lang=lang, tld=tld).save(out_mp3)
                        st.session_state["last_t2a_mp3"] = out_mp3

            if st.session_state.get("last_t2a_mp3") and os.path.exists(st.session_state["last_t2a_mp3"]):
                mp3_f = st.session_state["last_t2a_mp3"]
                st.audio(mp3_f)
                with open(mp3_f, "rb") as f:
                    st.download_button("⬇️ Download MP3", data=f, file_name=os.path.basename(mp3_f), mime="audio/mpeg", use_container_width=True)

        # =========================================================
        # TAB: ABOUT US
        # =========================================================
        elif active == "ABOUT US":
            st.markdown("""
            <div style="background: rgba(255, 240, 246, 0.94); border: 2px solid #6b0f2b; border-radius: 22px; padding: 1.6rem; color: #590d22;">
                <h3 style="margin-top:0;">🎀 About Mad Studios</h3>
                <p style="font-size:1.05rem; line-height:1.6;">
                    <b>Mad Studios</b> is an all-in-one AI creative studio built for modern short-form storytellers, animators, and digital creators.
                    Designed around our signature underwater reef aesthetic and cute animated mascot <b>Maddy</b>, Mad Studios turns simple text ideas into
                    expressive <b>9:16 YouTube Shorts & Instagram Reels</b>, 3D Pixar-style character art, and lifelike voiceovers in minutes.
                </p>
                <p style="font-size:1.05rem; line-height:1.6; margin-bottom:0;">
                    Whether you are brainstorming viral hooks with <b>Maddy's Octopus Bot</b>, transcribing clips, or producing full lip-synced animated episodes,
                    everything lives inside one joyful, distraction-free workspace.
                </p>
            </div>
            """, unsafe_allow_html=True)

        # =========================================================
        # TAB: WHY CHOOSE US
        # =========================================================
        elif active == "WHY CHOOSE US":
            st.markdown("""
            <div style="background: rgba(255, 240, 246, 0.94); border: 2px solid #6b0f2b; border-radius: 22px; padding: 1.6rem; color: #590d22;">
                <h3 style="margin-top:0;">✨ Why Choose Mad Studios?</h3>
                <ul style="font-size:1.05rem; line-height:1.8;">
                    <li><b>Consistent Character Identity:</b> Keeps Maddy's signature look, bindi, and 3D Pixar charm across every scene and image.</li>
                    <li><b>Built for 9:16 Vertical Video:</b> Native vertical framing, expressive full-body animation, and clean lip-sync ready for Shorts & Reels.</li>
                    <li><b>All-in-One Creator Workflow:</b> Brainstorm scripts, generate voices, render 3D art, transcribe videos, and store projects permanently in one place.</li>
                    <li><b>Zero-Clutter Studio UI:</b> Playful underwater home hub that switches instantly into a clean, focused production workspace.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        elif active == "YOUR WORK":
            sel_p = st.session_state.get("selected_work")
            if sel_p and os.path.exists(sel_p):
                st.subheader(f"📂 {os.path.basename(sel_p)}")
                v_left, v_mid, v_right = st.columns([0.8, 1.8, 0.8])
                with v_mid:
                    if sel_p.endswith(".mp4"):
                        st.video(sel_p)
                        with open(sel_p, "rb") as f:
                            st.download_button("⬇️ Download Reel (.mp4)", data=f, file_name=os.path.basename(sel_p), mime="video/mp4", type="primary", use_container_width=True)
                    else:
                        st.image(sel_p, use_container_width=True)
                        with open(sel_p, "rb") as f:
                            st.download_button("⬇️ Download Image (.png)", data=f, file_name=os.path.basename(sel_p), mime="image/png", type="primary", use_container_width=True)
            else:
                st.info("Pick any saved Reel or Image from 📁 Your Projects in the top-right corner!")


