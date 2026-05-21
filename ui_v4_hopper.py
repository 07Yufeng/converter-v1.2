import streamlit as st
from converter_toolpath_v4_hopper import convert_hp_to_mpf_text, get_conversion_report, normalize_power_head

st.set_page_config(page_title="HP/LST to MPF Converter", layout="wide")
st.title("TRUMPF HP/LST to BEaM MPF Converter v1.2")

st.sidebar.header("Conversion Settings")
power_head_label = st.sidebar.radio(
    "Select laser power head",
    ["10Vx", "24Vx"],
    index=1,
    help="This controls the PUIS_SET formula and BEaM gas settings."
)
power_head = normalize_power_head(power_head_label)
st.sidebar.markdown("""
**Power formula used**

- **10Vx**: `(POWER + 194.55) / 22.487`
- **24Vx**: `(POWER + 165.73) / 21.832`
""")

hopper_label = st.sidebar.selectbox(
    "Select hopper for use",
    ["Hopper 1", "Hopper 2", "Hopper 3", "Hopper 4", "Hopper 5"],
    index=2,
    help="Hopper selection"
)
selected_hopper = int(hopper_label.split()[-1])

uploaded_file = st.file_uploader("Upload original .HP or .LST file", type=["hp", "lst", "txt"])

if "hp_text" not in st.session_state:
    st.session_state.hp_text = ""
if "source_name" not in st.session_state:
    st.session_state.source_name = "uploaded.HP"
if "last_uploaded_name" not in st.session_state:
    st.session_state.last_uploaded_name = None
if "mpf_text" not in st.session_state:
    st.session_state.mpf_text = ""
if "report" not in st.session_state:
    st.session_state.report = None
if "last_power_head" not in st.session_state:
    st.session_state.last_power_head = power_head
if "last_selected_hopper" not in st.session_state:
    st.session_state.last_selected_hopper = selected_hopper

if uploaded_file is not None:
    uploaded_text = uploaded_file.read().decode("utf-8", errors="replace")
    if uploaded_file.name != st.session_state.last_uploaded_name:
        st.session_state.hp_text = uploaded_text
        st.session_state.source_name = uploaded_file.name
        st.session_state.last_uploaded_name = uploaded_file.name
        st.session_state.mpf_text = ""
        st.session_state.report = None

if power_head != st.session_state.last_power_head or selected_hopper != st.session_state.last_selected_hopper:
    st.session_state.last_power_head = power_head
    st.session_state.last_selected_hopper = selected_hopper
    st.session_state.mpf_text = ""
    st.session_state.report = None

if st.session_state.hp_text:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Editable HP/LST Input")
        st.caption("Edit the uploaded source code before conversion. The converter parses the edited text, including toolpath commands.")
        edited_text = st.text_area("Edit source code before conversion", value=st.session_state.hp_text, height=650, key="hp_editor")
        st.session_state.hp_text = edited_text
    with col2:
        st.subheader("Converted MPF Output")
        st.caption(f"Selected power head: **{power_head_label}** | Selected hopper: **{hopper_label}**")
        if st.button("Convert edited HP/LST to MPF", type="primary"):
            try:
                st.session_state.mpf_text = convert_hp_to_mpf_text(
                    st.session_state.hp_text,
                    source_name=st.session_state.source_name,
                    power_head=power_head,
                    selected_hopper=selected_hopper
                )
                st.session_state.report = get_conversion_report(
                    st.session_state.hp_text,
                    source_name=st.session_state.source_name,
                    power_head=power_head,
                    selected_hopper=selected_hopper
                )
                st.success("Conversion completed.")
            except Exception as e:
                st.session_state.mpf_text = ""
                st.session_state.report = None
                st.error(f"Conversion failed: {e}")
        if st.session_state.report:
            with st.expander("Conversion report", expanded=False):
                st.json(st.session_state.report)
        if st.session_state.mpf_text:
            st.text_area("Generated MPF", value=st.session_state.mpf_text, height=650)
            output_name = st.session_state.source_name.rsplit(".", 1)[0] + f"_{power_head}_converted.MPF"
            st.download_button("Download MPF file", data=st.session_state.mpf_text, file_name=output_name, mime="text/plain")
else:
    st.info("Upload a .HP or .LST file to begin.")
