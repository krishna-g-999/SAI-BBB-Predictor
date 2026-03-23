import streamlit as st
import os, sys, json, warnings
import requests as req
warnings.filterwarnings("ignore")

st.set_page_config(page_title="SAI BBB Predictor | SSSIHL", page_icon="🧠",
                   layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{font-family:'Inter',system-ui,sans-serif!important}
[data-testid="stAppViewContainer"]{background:#EEF2F9!important}
[data-testid="stSidebar"],[data-testid="collapsedControl"]{display:none}
.block-container{padding:0!important;max-width:100%!important}
header[data-testid="stHeader"]{display:none}
.sainet-header{background:linear-gradient(135deg,#040E1C 0%,#112A47 100%);
  border-bottom:3px solid #F0A500;padding:1.1rem 2.2rem;
  display:flex;align-items:center;gap:1.4rem;width:100%}
.ll img,.lr img{border-radius:50%}
.ll img{width:86px;height:86px;border:2.5px solid #F0A500;box-shadow:0 0 14px rgba(240,165,0,.35)}
.lr img{width:80px;height:80px;background:white;padding:4px;border:2px solid rgba(255,255,255,.25)}
.divider{width:2px;height:64px;background:linear-gradient(to bottom,transparent,#F0A500,transparent);flex-shrink:0}
.title-block{flex:1}
.sainet-header h1{color:white;font-size:2.2rem;font-weight:800;margin:0;letter-spacing:-.5px}
.sainet-header h1 span{color:#F0A500}
.subtitle{color:rgba(255,255,255,.72);font-size:.88rem;margin-top:.25rem}
.chip-row{display:flex;flex-wrap:wrap;gap:.4rem;margin-top:.6rem}
.chip{background:rgba(255,255,255,.1);color:rgba(255,255,255,.8);border:1px solid rgba(255,255,255,.2);border-radius:20px;padding:.22rem .75rem;font-size:.80rem}
.stat-box{text-align:right}
.stat-num{color:#F0A500;font-size:1.7rem;font-weight:800;display:block}
.stat-lbl{color:rgba(255,255,255,.55);font-size:.69rem;font-weight:800;text-transform:uppercase;letter-spacing:1.6px}
.stTabs [data-baseweb="tab-list"]{background:#F0F5FB!important;border-bottom:1px solid #D1DCF0;padding:0 2.2rem;gap:0}
.stTabs [data-baseweb="tab"]{color:#5A7299!important;font-size:.93rem!important;font-weight:600!important;padding:.75rem 1.4rem!important;border-bottom:3px solid transparent!important;background:transparent!important}
.stTabs [aria-selected="true"]{color:#0D2137!important;border-bottom:3px solid #F0A500!important}
.stTabs [data-baseweb="tab-panel"]{padding:2rem 2.2rem!important}
.sec-h{font-size:1.05rem;font-weight:700;color:#0D2137;margin-bottom:.2rem}
.sec-s{font-size:.89rem;color:#4A6080;margin-bottom:1.2rem}
.search-card{background:white;border-radius:12px;padding:1.6rem 1.8rem;margin-bottom:1.4rem;box-shadow:0 2px 12px rgba(4,14,28,.07)}
.pred-card{background:white;border-radius:10px;padding:1.1rem 1.3rem;margin-bottom:.85rem;box-shadow:0 2px 8px rgba(4,14,28,.06)}
.pred-label{font-size:.68rem;font-weight:800;text-transform:uppercase;letter-spacing:1.6px;color:#94A3B8;margin-bottom:.3rem}
.pred-value{font-size:1.55rem;font-weight:700;color:#0D2137}
.pred-sub{font-size:.80rem;color:#64748B;margin-top:.2rem}
.bar-wrap{background:#EEF2F9;border-radius:5px;height:7px;margin:6px 0 3px}
.bar-fill{height:7px;border-radius:5px}
.verdict-p{background:#E6F5EE;color:#1B6B45;border:1px solid #A7D7BC;border-radius:8px;padding:.9rem 1.2rem;margin-bottom:.8rem}
.verdict-e{background:#FFF3E0;color:#9B5C00;border:1px solid #F5C97A;border-radius:8px;padding:.9rem 1.2rem;margin-bottom:.8rem}
.verdict-r{background:#FDE8EA;color:#9B2335;border:1px solid #F5AABA;border-radius:8px;padding:.9rem 1.2rem;margin-bottom:.8rem}
.about-card{background:white;border-radius:12px;padding:1.8rem 2rem;box-shadow:0 2px 12px rgba(4,14,28,.07);margin-bottom:1.2rem}
.quote-block{border-left:3px solid #F0A500;background:#FFFBF0;padding:.9rem 1.2rem;border-radius:0 8px 8px 0;font-style:italic;color:#4A3000;margin-bottom:.85rem}
.quote-attr{font-size:.78rem;font-weight:700;color:#F0A500;text-transform:uppercase;letter-spacing:1px;margin-top:.4rem}
.person-card{background:#F8FAFD;border:1px solid #D8E4F0;border-radius:8px;padding:.9rem 1.2rem;margin-bottom:.6rem;display:flex;align-items:center;gap:.8rem}
.person-name{font-size:.95rem;font-weight:700;color:#0D2137}
.person-inst{font-size:.82rem;color:#5A7299}
.role-badge{display:inline-block;padding:.2rem .6rem;border-radius:5px;font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.8px}
.badge-pi{background:#1A3A5C;color:white}
.badge-dev{background:#F0A500;color:#040E1C}
.stButton>button{background:linear-gradient(135deg,#F0A500,#D4920A)!important;color:#040E1C!important;border:none!important;border-radius:8px!important;font-weight:700!important;font-size:.95rem!important;padding:.6rem 1.8rem!important;width:100%!important}
[data-testid="stTextInput"] input{background:#0D1F35!important;color:white!important;border:1px solid #2A4A6A!important;border-radius:8px!important;font-size:.93rem!important}
[data-testid="stTextInput"] input::placeholder{color:#6A8BAA!important}
.disclaimer{background:#F0F5FB;border:1px solid #C5D7F0;border-radius:8px;padding:.65rem 1rem;font-size:.80rem;color:#4A6080;margin-top:1.2rem}
</style>
""", unsafe_allow_html=True)

def logo_b64(path):
    import base64
    if os.path.exists(path):
        ext = path.rsplit(".",1)[-1]
        return "data:image/{};base64,{}".format(ext, base64.b64encode(open(path,"rb").read()).decode())
    return ""

ASSETS  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
SAI_SRC = logo_b64(os.path.join(ASSETS, "sai_net_logo.png"))
SSH_SRC = logo_b64(os.path.join(ASSETS, "sssihl_logo.png"))
ll = '<img src="{}">'.format(SAI_SRC) if SAI_SRC else '<div style="width:86px;height:86px;border-radius:50%;background:#1A3A5C;border:2.5px solid #F0A500"></div>'
lr = '<img src="{}">'.format(SSH_SRC) if SSH_SRC else '<div style="width:80px;height:80px;border-radius:50%;background:white"></div>'

st.markdown("""
<div class="sainet-header">
  <div class="ll">{ll}</div><div class="divider"></div>
  <div class="title-block">
    <h1>SAI <span>BBB</span> Predictor</h1>
    <div class="subtitle">CNS Drug Transport Prediction &nbsp;|&nbsp; A SAI-Net Translational Module</div>
    <div class="chip-row">
      <span class="chip">BBB Penetration</span><span class="chip">PGP Efflux</span>
      <span class="chip">BCRP &amp; MRP1</span><span class="chip">logBB</span>
      <span class="chip">PAMPA</span><span class="chip">Caco-2</span>
    </div>
  </div>
  <div style="flex:1"></div>
  <div class="stat-box"><span class="stat-num">7</span><span class="stat-lbl">Endpoints</span></div>
  <div class="divider" style="margin:0 1rem"></div>
  <div class="lr">{lr}</div>
</div>
""".format(ll=ll, lr=lr), unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def pubchem_lookup(name):
    try:
        url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{}/property/IsomericSMILES,IUPACName,MolecularWeight,MolecularFormula/JSON".format(req.utils.quote(name))
        r = req.get(url, timeout=8)
        if r.status_code != 200: return None
        p = r.json()["PropertyTable"]["Properties"][0]
        return {"smiles": p.get("IsomericSMILES",""), "iupac": p.get("IUPACName",""),
                "mw": p.get("MolecularWeight",""), "formula": p.get("MolecularFormula",""),
                "cid": p.get("CID","")}
    except: return None

@st.cache_resource(show_spinner="Loading SAI-Net v3 ensemble...")
def load_models():
    import torch
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from sainet_model import SAINetV2
    MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
    SEEDS = [42, 123, 456, 789, 2026]
    if not os.path.isdir(MODEL_DIR) or not any(
        os.path.exists(os.path.join(MODEL_DIR, "seed_{}_best_model.pt".format(s))) for s in SEEDS):
        try:
            from huggingface_hub import hf_hub_download
            import shutil
            os.makedirs(MODEL_DIR, exist_ok=True)
            HF = os.environ.get("HF_REPO", "Krishnasalini/SAI-Net-v3")
            for s in SEEDS:
                fn = "seed_{}_best_model.pt".format(s)
                shutil.copy(hf_hub_download(repo_id=HF, filename=fn,
                            cache_dir="/tmp/sainet_cache"),
                            os.path.join(MODEL_DIR, fn))
        except Exception as e:
            return None, None, str(e)
    models, loaded = [], []
    for s in SEEDS:
        ck = os.path.join(MODEL_DIR, "seed_{}_best_model.pt".format(s))
        if not os.path.exists(ck): continue
        try:
            state = torch.load(ck, map_location="cpu")
            sd = state.get("model_state_dict", state) if isinstance(state, dict) else state
            m = SAINetV2(); m.load_state_dict(sd, strict=True); m.eval()
            models.append(m); loaded.append(s)
        except: pass
    return models, loaded, None

def predict(smiles, models):
    import torch, numpy as np
    from torch_geometric.data import Data
    from rdkit import Chem
    from sainet_model import atom_feat, bond_feat
    ALL  = ["BBB","logBB","PGP","BCRP","MRP1","PAMPA","Caco2","LogP","PPBR","CYP3A4","CYP2C19","CYP1A2"]
    CLS  = {"BBB","PGP","BCRP","MRP1","CYP3A4","CYP2C19","CYP1A2"}
    SHOW = ["BBB","PGP","BCRP","MRP1","logBB","PAMPA","Caco2"]
    mol = Chem.MolFromSmiles(smiles)
    if mol is None: return None
    x = torch.tensor([atom_feat(a) for a in mol.GetAtoms()], dtype=torch.float)
    src, dst, ea = [], [], []
    for b in mol.GetBonds():
        i, j = b.GetBeginAtomIdx(), b.GetEndAtomIdx()
        bf = bond_feat(b)
        src += [i,j]; dst += [j,i]; ea += [bf,bf]
    if not src: return None
    data = Data(x=x, edge_index=torch.tensor([src,dst], dtype=torch.long),
                edge_attr=torch.tensor(ea, dtype=torch.float))
    data.batch = torch.zeros(x.shape[0], dtype=torch.long)
    preds = []
    with torch.no_grad():
        for m in models:
            out = m(data).cpu().numpy().flatten()
            preds.append([1/(1+np.exp(-float(out[i]))) if t in CLS else float(out[i])
                          for i,t in enumerate(ALL) if i < len(out)])
    mn = np.mean(preds, axis=0); sd = np.std(preds, axis=0)
    return {t: {"mean": round(float(mn[ALL.index(t)]),4), "std": round(float(sd[ALL.index(t)]),4)} for t in SHOW}

def mol_img(smi):
    try:
        from rdkit import Chem; from rdkit.Chem import Draw; import io
        buf = io.BytesIO()
        Draw.MolToImage(Chem.MolFromSmiles(smi), size=(260,190)).save(buf, "PNG")
        buf.seek(0); return buf
    except: return None

def cns_rules(smi):
    try:
        from rdkit import Chem; from rdkit.Chem import Descriptors, rdMolDescriptors
        mol = Chem.MolFromSmiles(smi)
        if mol is None: return {}
        return {
            "MW":   ("{:.0f} Da".format(Descriptors.MolWt(mol)),   Descriptors.MolWt(mol) <= 450),
            "LogP": ("{:.2f}".format(Descriptors.MolLogP(mol)),    -0.5 <= Descriptors.MolLogP(mol) <= 5.0),
            "TPSA": ("{:.0f} A2".format(rdMolDescriptors.CalcTPSA(mol)), rdMolDescriptors.CalcTPSA(mol) <= 90),
            "HBD":  ("{}".format(rdMolDescriptors.CalcNumHBD(mol)), rdMolDescriptors.CalcNumHBD(mol) <= 3),
            "HBA":  ("{}".format(rdMolDescriptors.CalcNumHBA(mol)), rdMolDescriptors.CalcNumHBA(mol) <= 7),
        }
    except: return {}

tab1, tab2 = st.tabs(["Compound Search", "About SAI-Net"])

with tab1:
    st.markdown('<div class="sec-h">Search a Compound</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-s">Enter any drug name or approved compound. The tool retrieves the structure from PubChem and predicts all 7 CNS transport endpoints using SAI-Net v3.</div>', unsafe_allow_html=True)
    st.markdown('<div class="search-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([5,1])
    name = c1.text_input("n", placeholder="Type any compound — e.g. donepezil, edaravone, memantine, curcumin...", label_visibility="collapsed")
    run  = c2.button("View Report")
    st.markdown("""
    <div style="margin-top:.6rem;font-size:.78rem;color:#94A3B8;font-weight:800;text-transform:uppercase;letter-spacing:1px;margin-bottom:.35rem">Suggested compounds</div>
    <div class="chip-row">
      <span class="chip" style="background:#EEF4FF;color:#1A3A5C;border-color:#C5D7F0">Donepezil</span>
      <span class="chip" style="background:#EEF4FF;color:#1A3A5C;border-color:#C5D7F0">Edaravone</span>
      <span class="chip" style="background:#EEF4FF;color:#1A3A5C;border-color:#C5D7F0">Riluzole</span>
      <span class="chip" style="background:#EEF4FF;color:#1A3A5C;border-color:#C5D7F0">Memantine</span>
      <span class="chip" style="background:#EEF4FF;color:#1A3A5C;border-color:#C5D7F0">Ibuprofen</span>
      <span class="chip" style="background:#EEF4FF;color:#1A3A5C;border-color:#C5D7F0">Curcumin</span>
      <span class="chip" style="background:#EEF4FF;color:#1A3A5C;border-color:#C5D7F0">Resveratrol</span>
    </div></div>""", unsafe_allow_html=True)

    if run and name.strip():
        with st.spinner("Looking up {} on PubChem...".format(name)):
            cmpd = pubchem_lookup(name.strip())
        if cmpd is None:
            st.error("**{}** not found on PubChem. Try the generic or IUPAC name.".format(name)); st.stop()

        st.markdown("""
        <div style="background:linear-gradient(135deg,#0D1F35,#1A3A5C);border-radius:10px;
          padding:1.2rem 1.6rem;margin-bottom:1.2rem;border-left:4px solid #F0A500">
          <div style="color:#F0A500;font-size:.72rem;font-weight:800;text-transform:uppercase;letter-spacing:1.4px">Compound identified</div>
          <div style="color:white;font-size:1.6rem;font-weight:800;margin:.25rem 0 .1rem">{name}</div>
          <div style="color:rgba(255,255,255,.65);font-size:.82rem">{iupac}</div>
          <div style="display:flex;gap:1.4rem;margin-top:.6rem;flex-wrap:wrap">
            <span style="color:rgba(255,255,255,.6);font-size:.80rem">MW: <b style="color:white">{mw} Da</b></span>
            <span style="color:rgba(255,255,255,.6);font-size:.80rem">Formula: <b style="color:white">{formula}</b></span>
            <span style="color:rgba(255,255,255,.6);font-size:.80rem">PubChem CID: <b style="color:#F0A500">{cid}</b></span>
          </div>
        </div>""".format(name=name.title(), iupac=cmpd["iupac"], mw=cmpd["mw"],
                         formula=cmpd["formula"], cid=cmpd["cid"]), unsafe_allow_html=True)

        models, loaded, err = load_models()
        if err or not models:
            st.error("Model loading failed: {}".format(err or "no checkpoints")); st.stop()

        with st.spinner("Running SAI-Net v3 ensemble prediction..."):
            result = predict(cmpd["smiles"], models)
        if result is None:
            st.error("Prediction failed. Compound may not be compatible."); st.stop()

        cs, cc, cr = st.columns([1.3, 2.4, 2.3])

        with cs:
            st.markdown('<div class="pred-label">2D Structure</div>', unsafe_allow_html=True)
            buf = mol_img(cmpd["smiles"])
            if buf: st.image(buf, use_container_width=True)
            st.markdown('<div class="pred-label" style="margin-top:1rem">CNS Property Rules</div>', unsafe_allow_html=True)
            for prop, (val, ok) in cns_rules(cmpd["smiles"]).items():
                c, bg = ("#1B6B45","#E6F5EE") if ok else ("#9B2335","#FDE8EA")
                icon = "&#10003;" if ok else "&#10007;"
                st.markdown("""<div style="display:flex;justify-content:space-between;
                  padding:.4rem .7rem;background:{bg};border-radius:6px;margin-bottom:.3rem">
                  <span style="font-size:.82rem;font-weight:600;color:{c}">{prop}</span>
                  <span style="font-size:.82rem;font-weight:700;color:{c}">{icon} {val}</span>
                </div>""".format(bg=bg, c=c, prop=prop, icon=icon, val=val), unsafe_allow_html=True)

        with cc:
            st.markdown('<div class="sec-h">Classification Endpoints</div>', unsafe_allow_html=True)
            for k, lbl, tip in [
                ("BBB",  "BBB Penetration",  "Probability of crossing the blood-brain barrier"),
                ("PGP",  "PGP Efflux",       "P-glycoprotein efflux substrate"),
                ("BCRP", "BCRP Efflux",      "Breast cancer resistance protein efflux"),
                ("MRP1", "MRP1 Efflux",      "Multidrug resistance protein 1 efflux"),
            ]:
                v = result[k]["mean"]; pct = v * 100
                fc, bg = ("#1B6B45","#E6F5EE") if pct < 40 else (("#9B5C00","#FFF3E0") if pct < 70 else ("#9B2335","#FDE8EA"))
                st.markdown("""<div class="pred-card">
                  <div class="pred-label">{lbl}</div>
                  <div class="pred-value" style="color:{fc}">{pct:.1f}%</div>
                  <div class="bar-wrap"><div class="bar-fill" style="width:{pct2:.0f}%;background:{fc}"></div></div>
                  <div class="pred-sub">{tip} &middot; &sigma; &plusmn;{std:.1f}%</div>
                </div>""".format(lbl=lbl, fc=fc, pct=pct, pct2=min(pct,100),
                                 tip=tip, std=result[k]["std"]*100), unsafe_allow_html=True)

        with cr:
            st.markdown('<div class="sec-h">Regression Endpoints</div>', unsafe_allow_html=True)
            for k, lbl, tip in [
                ("logBB", "log(Brain / Blood)", "logBB > +0.30 indicates CNS penetration"),
                ("PAMPA", "PAMPA log Pe",       "Passive membrane permeability"),
                ("Caco2", "Caco-2 log Papp",    "Intestinal absorption permeability"),
            ]:
                v = result[k]["mean"]
                st.markdown("""<div class="pred-card">
                  <div class="pred-label">{lbl}</div>
                  <div class="pred-value">{v:+.3f}</div>
                  <div class="pred-sub">{tip} &middot; &sigma; &plusmn;{std:.3f}</div>
                </div>""".format(lbl=lbl, v=v, tip=tip, std=result[k]["std"]), unsafe_allow_html=True)

            bbb = result["BBB"]["mean"]; pgp = result["PGP"]["mean"]; lbb = result["logBB"]["mean"]
            if bbb >= 0.5 and lbb >= 0.30 and pgp < 0.5:
                vc, vt, vb = "p", "CNS-PENETRANT", "High probability of brain exposure &middot; BBB {:.0%} &middot; logBB {:+.2f}".format(bbb, lbb)
            elif bbb >= 0.5 and pgp >= 0.5:
                vc, vt, vb = "e", "EFFLUX LIMITED", "Penetrates but subject to efflux &middot; PGP {:.0%}".format(pgp)
            else:
                vc, vt, vb = "r", "CNS-RESTRICTED", "Low predicted brain exposure &middot; BBB {:.0%} &middot; logBB {:+.2f}".format(bbb, lbb)
            st.markdown("""<div class="verdict-{vc}">
              <div style="font-size:.70rem;font-weight:800;text-transform:uppercase;letter-spacing:1.4px;margin-bottom:.3rem">CNS Profile Verdict</div>
              <div style="font-size:1.05rem;font-weight:700">{vt}</div>
              <div style="font-size:.82rem;margin-top:.2rem">{vb}</div>
            </div>""".format(vc=vc, vt=vt, vb=vb), unsafe_allow_html=True)

        st.download_button("Download Full Report (JSON)",
            data=json.dumps({"compound": name, "pubchem_cid": cmpd["cid"],
                             "predictions": {k: v["mean"] for k,v in result.items()},
                             "std": {k: v["std"] for k,v in result.items()}}, indent=2),
            file_name="sainet_{}.json".format(name.lower().replace(" ","_")),
            mime="application/json")
        st.markdown('<div class="disclaimer"><b>Educational Purpose Only</b> - Not intended as medical advice. Predictions are computational estimates only.</div>', unsafe_allow_html=True)

    elif run:
        st.warning("Please enter a compound name before clicking View Report.")

with tab2:
    cl, ct = st.columns([1,3])
    with cl:
        if SAI_SRC:
            st.markdown('<div style="padding:1rem"><img src="{}" style="width:160px;height:160px;border-radius:50%;border:3px solid #F0A500;box-shadow:0 0 20px rgba(240,165,0,.3)"></div>'.format(SAI_SRC), unsafe_allow_html=True)
    with ct:
        st.markdown("""<div class="about-card">
          <div style="font-size:1.6rem;font-weight:800;color:#0D2137;margin-bottom:.3rem">About <span style="color:#F0A500">SAI BBB</span> Predictor</div>
          <div style="background:#F0A500;height:3px;width:60px;border-radius:2px;margin-bottom:1rem"></div>
          <div style="font-size:.82rem;font-weight:800;text-transform:uppercase;letter-spacing:1.4px;color:#F0A500;margin-bottom:.4rem">SCIENCE FOR SOCIETY</div>
          <div style="color:#4A6080;font-size:.92rem">Advancing CNS drug discovery through computational intelligence.</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="about-card">
      <div style="font-size:1.05rem;font-weight:700;color:#0D2137;margin-bottom:.8rem">SAI-Net Connection</div>
      <p style="color:#334155;font-size:.89rem;line-height:1.7">SAI BBB Predictor is a <b>translational web module</b> derived from <b>SAI-Net v3</b> - a multitask graph attention network for simultaneous prediction of seven CNS transport endpoints from molecular structure.</p>
      <div style="background:#EEF4FF;border-radius:8px;padding:.8rem 1rem;margin-top:.6rem;border-left:3px solid #1A3A5C">
        <b style="color:#1A3A5C;font-size:.85rem">Target Publication:</b>
        <span style="color:#334155;font-size:.85rem"> Nucleic Acids Research - Web Server Issue 2026</span>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="about-card">
      <div style="font-size:1.05rem;font-weight:700;color:#0D2137;margin-bottom:1rem">100 Years of Selfless Service</div>
      <div class="quote-block">"Let the world achieve the glory of becoming a family - through Love."
        <div class="quote-attr">- Bhagawan Sri Sathya Sai Baba</div></div>
      <div class="quote-block">"True knowledge is that which makes man work for the welfare of humanity."
        <div class="quote-attr">- Bhagawan Sri Sathya Sai Baba</div></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="about-card">
      <div style="font-size:1.05rem;font-weight:700;color:#0D2137;margin-bottom:1rem">Research Team</div>
      <div class="person-card">
        <span class="role-badge badge-pi">Principal Investigator</span>
        <div><div class="person-name">Prof. Venketesh Sivaramakrishnan</div>
        <div class="person-inst">Sri Sathya Sai Institute of Higher Learning</div></div>
      </div>
      <div class="person-card">
        <span class="role-badge badge-dev">Developer</span>
        <div><div class="person-name">Krishnasalini Gunanathan</div>
        <div class="person-inst">Sri Sathya Sai Institute of Higher Learning</div></div>
      </div>
    </div>
    <div class="disclaimer"><b>Educational Purpose Only</b> - Not intended as medical advice.</div>
    """, unsafe_allow_html=True)
