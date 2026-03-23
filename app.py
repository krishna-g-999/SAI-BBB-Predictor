import streamlit as st
import os, sys, json, warnings
import urllib.parse, urllib.request, ssl
warnings.filterwarnings("ignore")

st.set_page_config(page_title="SAI BBB Predictor | SSSIHL", page_icon=chr(0x1F9E0),
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
.divider{width:2px;height:64px;background:linear-gradient(to bottom,transparent,#F0A500,transparent);flex-shrink:0}
.title-block{flex:1}
.sainet-header h1{font-size:2.2rem;font-weight:800;margin:0;letter-spacing:-.5px}
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
.input-card{background:white;border-radius:12px;padding:1.6rem 1.8rem;margin-bottom:1.4rem;box-shadow:0 2px 12px rgba(4,14,28,.07)}
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
.smiles-ex{font-family:monospace;font-size:.78rem;color:#1A3A5C;background:#EEF4FF;padding:.15rem .45rem;border-radius:4px}
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
ll = '<img src="{}" style="width:86px;height:86px;border-radius:50%;border:2.5px solid #F0A500">'.format(SAI_SRC) if SAI_SRC else '<div style="width:86px;height:86px;border-radius:50%;background:#1A3A5C;border:2.5px solid #F0A500"></div>'
lr = '<img src="{}" style="width:80px;height:80px;border-radius:50%;background:white;padding:4px">'.format(SSH_SRC) if SSH_SRC else '<div style="width:80px;height:80px;border-radius:50%;background:white"></div>'

st.markdown("""
<div class="sainet-header">
  <div>{ll}</div><div class="divider"></div>
  <div class="title-block">
    <h1><span style="color:white">SAI</span><span style="color:#F0A500"> BBB</span> <span style="color:white;font-weight:400;font-size:1.6rem">Predictor</span></h1>
    <div class="subtitle">CNS Drug Transport Prediction &nbsp;|&nbsp; SSSIHL Biosciences</div>
    <div class="chip-row">
      <span class="chip">BBB Penetration</span><span class="chip">PGP Efflux</span>
      <span class="chip">BCRP &amp; MRP1</span><span class="chip">logBB</span>
      <span class="chip">PAMPA</span><span class="chip">Caco-2</span>
    </div>
  </div>
  <div style="flex:1"></div>
  <div class="stat-box"><span class="stat-num">7</span><span class="stat-lbl">Endpoints</span></div>
  <div class="divider" style="margin:0 1rem"></div>
  <div>{lr}</div>
</div>
""".format(ll=ll, lr=lr), unsafe_allow_html=True)

# ── PubChem helper (optional, graceful fallback) ─────────────────────────────
def pubchem_lookup(name):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    encoded = urllib.parse.quote(name.strip())
    url = ("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
           + encoded
           + "/property/IsomericSMILES,IUPACName,MolecularWeight,MolecularFormula/JSON")
    try:
        with urllib.request.urlopen(url, timeout=10, context=ctx) as resp:
            import json as _j
            data = _j.loads(resp.read().decode())
        p = data["PropertyTable"]["Properties"][0]
        return {"smiles": p.get("IsomericSMILES",""), "iupac": p.get("IUPACName",""),
                "mw": str(p.get("MolecularWeight","")), "formula": p.get("MolecularFormula",""),
                "cid": str(p.get("CID",""))}
    except:
        return None

# ── Model loading ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading SAI BBB model...")
def load_models():
    import torch
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from sainet_model import SAINetV2
    except Exception as e:
        return None, None, "Import failed: " + str(e)
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
                shutil.copy(hf_hub_download(repo_id=HF, filename=fn, cache_dir="/tmp/sainet_cache"),
                            os.path.join(MODEL_DIR, fn))
        except Exception as e:
            return None, None, "HF download failed: " + str(e)
    models, loaded = [], []
    for s in SEEDS:
        ck = os.path.join(MODEL_DIR, "seed_{}_best_model.pt".format(s))
        if not os.path.exists(ck): continue
        try:
            import torch
            state = torch.load(ck, map_location="cpu", weights_only=False)
            sd = state.get("model_state_dict", state) if isinstance(state, dict) else state
            m = SAINetV2(); m.load_state_dict(sd, strict=True); m.eval()
            models.append(m); loaded.append(s)
        except Exception as e:
            pass
    if not models:
        return None, None, "No checkpoints loaded from " + MODEL_DIR
    return models, loaded, None

# ── Prediction ────────────────────────────────────────────────────────────────
def predict(smiles, models):
    import torch, numpy as np
    from torch_geometric.data import Data
    from rdkit import Chem
    import sainet_model as sm
    ALL  = ["BBB","logBB","PGP","BCRP","MRP1","PAMPA","Caco2","LogP","PPBR","CYP3A4","CYP2C19","CYP1A2"]
    CLS  = {"BBB","PGP","BCRP","MRP1","CYP3A4","CYP2C19","CYP1A2"}
    SHOW = ["BBB","PGP","BCRP","MRP1","logBB","PAMPA","Caco2"]
    af = getattr(sm, "atom_feat", None)
    bf = getattr(sm, "bond_feat", None)
    if not af or not bf:
        return None, "atom_feat/bond_feat missing in sainet_model"
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None, "Invalid SMILES — RDKit could not parse structure"
        x = torch.tensor([af(a) for a in mol.GetAtoms()], dtype=torch.float)
        src, dst, ea = [], [], []
        for b in mol.GetBonds():
            i, j = b.GetBeginAtomIdx(), b.GetEndAtomIdx()
            bfeat = bf(b)
            src += [i,j]; dst += [j,i]; ea += [bfeat, bfeat]
        if not src:
            return None, "Molecule has no bonds"
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
        return {t: {"mean": round(float(mn[ALL.index(t)]),4),
                    "std":  round(float(sd[ALL.index(t)]),4)} for t in SHOW}, None
    except Exception as e:
        return None, str(e)

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

# ── UI ────────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Compound Search", "About SAI BBB"])

with tab1:
    st.markdown('<div class="sec-h">Predict CNS Transport</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-s">Enter a SMILES string directly, or use a compound name to auto-fetch structure from PubChem.</div>', unsafe_allow_html=True)

    mode = st.radio("Input mode", ["SMILES (direct)", "Compound name (PubChem lookup)"],
                    horizontal=True, label_visibility="collapsed")

    smiles_input = ""
    compound_label = ""
    cmpd_meta = {}

    if mode == "SMILES (direct)":
        st.markdown("""
        <div style="font-size:.78rem;color:#64748B;margin-bottom:.4rem">
        Paste any valid SMILES string. Examples:
        <span class="smiles-ex">CC(=O)Oc1ccccc1C(=O)O</span> (aspirin) &nbsp;
        <span class="smiles-ex">CN1CCC[C@H]1c2cccnc2</span> (nicotine)
        </div>""", unsafe_allow_html=True)
        col1, col2 = st.columns([5,1])
        smiles_input = col1.text_input("smiles", placeholder="e.g. CC(=O)Oc1ccccc1C(=O)O",
                                       label_visibility="collapsed")
        run = col2.button("Predict")
        compound_label = smiles_input[:20] + "..." if len(smiles_input) > 20 else smiles_input

    else:
        st.markdown("""
        <div style="font-size:.78rem;color:#64748B;margin-bottom:.4rem">
        Suggested: <b>donepezil</b> &nbsp; <b>memantine</b> &nbsp; <b>riluzole</b> &nbsp; <b>curcumin</b>
        </div>""", unsafe_allow_html=True)
        col1, col2 = st.columns([5,1])
        name_input = col1.text_input("name", placeholder="e.g. donepezil",
                                     label_visibility="collapsed")
        run = col2.button("Predict")
        if run and name_input.strip():
            with st.spinner("Fetching structure from PubChem..."):
                cmpd_meta = pubchem_lookup(name_input.strip())
            if cmpd_meta:
                smiles_input   = cmpd_meta["smiles"]
                compound_label = name_input.title()
            else:
                st.error("**{}** not found on PubChem. Switch to SMILES mode and paste the structure directly.".format(name_input))
                st.markdown("""<div class="disclaimer">
                Tip: Get SMILES from <a href="https://pubchem.ncbi.nlm.nih.gov" target="_blank">PubChem</a>,
                <a href="https://www.chemspider.com" target="_blank">ChemSpider</a>, or your docking software.
                </div>""", unsafe_allow_html=True)
                st.stop()
        elif run:
            st.warning("Please enter a compound name."); st.stop()
        else:
            run = False

    if run and smiles_input.strip():
        # Show compound card
        if cmpd_meta:
            st.markdown("""
            <div style="background:linear-gradient(135deg,#0D1F35,#1A3A5C);border-radius:10px;
              padding:1.2rem 1.6rem;margin-bottom:1.2rem;border-left:4px solid #F0A500">
              <div style="color:#F0A500;font-size:.72rem;font-weight:800;text-transform:uppercase;letter-spacing:1.4px">Compound identified</div>
              <div style="color:white;font-size:1.6rem;font-weight:800;margin:.25rem 0 .1rem">{name}</div>
              <div style="color:rgba(255,255,255,.65);font-size:.82rem">{iupac}</div>
              <div style="display:flex;gap:1.4rem;margin-top:.6rem;flex-wrap:wrap">
                <span style="color:rgba(255,255,255,.6);font-size:.80rem">MW: <b style="color:white">{mw} Da</b></span>
                <span style="color:rgba(255,255,255,.6);font-size:.80rem">Formula: <b style="color:white">{formula}</b></span>
                <span style="color:rgba(255,255,255,.6);font-size:.80rem">CID: <b style="color:#F0A500">{cid}</b></span>
              </div>
            </div>""".format(name=compound_label, iupac=cmpd_meta.get("iupac",""),
                             mw=cmpd_meta.get("mw",""), formula=cmpd_meta.get("formula",""),
                             cid=cmpd_meta.get("cid","")), unsafe_allow_html=True)

        # Load and run model
        models, loaded, err = load_models()
        if err or not models:
            st.error("Model loading failed: {}".format(err or "no checkpoints found"))
            st.stop()

        with st.spinner("Running SAI BBB prediction..."):
            result, pred_err = predict(smiles_input.strip(), models)

        if result is None:
            st.error("Prediction failed: {}".format(pred_err))
            st.stop()

        # Results layout
        cs, cc, cr = st.columns([1.3, 2.4, 2.3])

        with cs:
            st.markdown('<div class="pred-label">2D Structure</div>', unsafe_allow_html=True)
            buf = mol_img(smiles_input.strip())
            if buf: st.image(buf, use_container_width=True)
            st.markdown('<div class="pred-label" style="margin-top:1rem">CNS Drug-likeness</div>', unsafe_allow_html=True)
            for prop, (val, ok) in cns_rules(smiles_input.strip()).items():
                c, bg = ("#1B6B45","#E6F5EE") if ok else ("#9B2335","#FDE8EA")
                icon  = "&#10003;" if ok else "&#10007;"
                st.markdown("""<div style="display:flex;justify-content:space-between;
                  padding:.4rem .7rem;background:{bg};border-radius:6px;margin-bottom:.3rem">
                  <span style="font-size:.82rem;font-weight:600;color:{c}">{prop}</span>
                  <span style="font-size:.82rem;font-weight:700;color:{c}">{icon} {val}</span>
                </div>""".format(bg=bg,c=c,prop=prop,icon=icon,val=val), unsafe_allow_html=True)

        with cc:
            st.markdown('<div class="sec-h">Classification</div>', unsafe_allow_html=True)
            for k, lbl, tip in [
                ("BBB",  "BBB Penetration",  "Probability of crossing the blood-brain barrier"),
                ("PGP",  "PGP Efflux",       "P-glycoprotein efflux substrate probability"),
                ("BCRP", "BCRP Efflux",      "Breast cancer resistance protein efflux"),
                ("MRP1", "MRP1 Efflux",      "Multidrug resistance protein 1 efflux"),
            ]:
                v = result[k]["mean"]; pct = v * 100
                fc = "#1B6B45" if pct < 40 else ("#9B5C00" if pct < 70 else "#9B2335")
                st.markdown("""<div class="pred-card">
                  <div class="pred-label">{lbl}</div>
                  <div class="pred-value" style="color:{fc}">{pct:.1f}%</div>
                  <div class="bar-wrap"><div class="bar-fill" style="width:{p2:.0f}%;background:{fc}"></div></div>
                  <div class="pred-sub">{tip} &middot; &sigma; &plusmn;{std:.1f}%</div>
                </div>""".format(lbl=lbl,fc=fc,pct=pct,p2=min(pct,100),tip=tip,
                                 std=result[k]["std"]*100), unsafe_allow_html=True)

        with cr:
            st.markdown('<div class="sec-h">Regression</div>', unsafe_allow_html=True)
            for k, lbl, tip in [
                ("logBB", "log(Brain/Blood)", "logBB > +0.30 = CNS penetrant"),
                ("PAMPA", "PAMPA log Pe",     "Passive membrane permeability"),
                ("Caco2", "Caco-2 log Papp",  "Intestinal absorption permeability"),
            ]:
                v = result[k]["mean"]
                st.markdown("""<div class="pred-card">
                  <div class="pred-label">{lbl}</div>
                  <div class="pred-value">{v:+.3f}</div>
                  <div class="pred-sub">{tip} &middot; &sigma; &plusmn;{std:.3f}</div>
                </div>""".format(lbl=lbl,v=v,tip=tip,std=result[k]["std"]), unsafe_allow_html=True)

            bbb = result["BBB"]["mean"]; pgp = result["PGP"]["mean"]; lbb = result["logBB"]["mean"]
            if bbb >= 0.5 and lbb >= 0.30 and pgp < 0.5:
                vc,vt,vb = "p","CNS-PENETRANT","BBB {:.0%}  logBB {:+.2f}".format(bbb,lbb)
            elif bbb >= 0.5 and pgp >= 0.5:
                vc,vt,vb = "e","EFFLUX LIMITED","PGP {:.0%}  BBB {:.0%}".format(pgp,bbb)
            else:
                vc,vt,vb = "r","CNS-RESTRICTED","BBB {:.0%}  logBB {:+.2f}".format(bbb,lbb)
            st.markdown("""<div class="verdict-{vc}">
              <div style="font-size:.70rem;font-weight:800;text-transform:uppercase;letter-spacing:1.4px;margin-bottom:.3rem">SAI BBB Verdict</div>
              <div style="font-size:1.05rem;font-weight:700">{vt}</div>
              <div style="font-size:.82rem;margin-top:.2rem">{vb}</div>
            </div>""".format(vc=vc,vt=vt,vb=vb), unsafe_allow_html=True)

        st.download_button("Download Report (JSON)",
            data=json.dumps({"smiles": smiles_input, "compound": compound_label,
                             "predictions": {k: v["mean"] for k,v in result.items()},
                             "std": {k: v["std"] for k,v in result.items()}}, indent=2),
            file_name="saibbb_{}.json".format(compound_label.lower().replace(" ","_").replace("/","")),
            mime="application/json")
        st.markdown('<div class="disclaimer"><b>Educational/Research Use Only</b> — Not for clinical decision making.</div>', unsafe_allow_html=True)

    elif run:
        st.warning("Please enter a SMILES string or compound name.")

with tab2:
    st.markdown("""<div class="about-card">
      <div style="font-size:1.6rem;font-weight:800;color:#0D2137">
        About <span style="color:white;background:#0D2137;padding:0 .3rem">SAI</span><span style="color:#F0A500"> BBB</span> Predictor</div>
      <div style="background:#F0A500;height:3px;width:60px;border-radius:2px;margin:.6rem 0 1rem"></div>
      <p style="color:#334155;font-size:.92rem;line-height:1.75">
        SAI BBB Predictor is a multitask deep learning tool for simultaneous prediction of
        7 CNS drug transport endpoints from molecular structure. It accepts both SMILES strings
        (for novel compounds) and compound names (via PubChem lookup), enabling use across
        virtual screening, lead optimisation, and ADMET profiling workflows.</p>
      <div style="background:#EEF4FF;border-radius:8px;padding:.8rem 1rem;margin-top:.8rem;border-left:3px solid #1A3A5C">
        <b style="color:#1A3A5C;font-size:.85rem">Target Publication:</b>
        <span style="color:#334155;font-size:.85rem"> Nucleic Acids Research — Web Server Issue 2026</span>
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown("""<div class="about-card">
      <div style="font-size:1.05rem;font-weight:700;color:#0D2137;margin-bottom:1rem">100 Years of Selfless Service</div>
      <div class="quote-block">"Let the world achieve the glory of becoming a family - through Love."
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
    <div class="disclaimer"><b>Educational Purpose Only</b> — Not intended as medical advice.</div>
    """, unsafe_allow_html=True)
