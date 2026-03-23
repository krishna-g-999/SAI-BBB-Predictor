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
.sainet-header h1{font-size:2.1rem;font-weight:800;margin:0;letter-spacing:-.5px;line-height:1.1}
.tagline{color:#F0A500;font-size:.80rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;margin-top:.18rem}
.subtitle{color:rgba(255,255,255,.60);font-size:.80rem;margin-top:.18rem}
.chip-row{display:flex;flex-wrap:wrap;gap:.35rem;margin-top:.55rem}
.chip{background:rgba(255,255,255,.08);color:rgba(255,255,255,.78);border:1px solid rgba(255,255,255,.18);border-radius:20px;padding:.18rem .65rem;font-size:.76rem}
.stat-box{text-align:right}
.stat-num{color:#F0A500;font-size:1.6rem;font-weight:800;display:block}
.stat-lbl{color:rgba(255,255,255,.45);font-size:.64rem;font-weight:800;text-transform:uppercase;letter-spacing:1.6px}
.stTabs [data-baseweb="tab-list"]{background:#F0F5FB!important;border-bottom:1px solid #D1DCF0;padding:0 2.2rem;gap:0}
.stTabs [data-baseweb="tab"]{color:#5A7299!important;font-size:.93rem!important;font-weight:600!important;padding:.75rem 1.4rem!important;border-bottom:3px solid transparent!important;background:transparent!important}
.stTabs [aria-selected="true"]{color:#0D2137!important;border-bottom:3px solid #F0A500!important}
.stTabs [data-baseweb="tab-panel"]{padding:2rem 2.2rem!important}
.sec-h{font-size:1.05rem;font-weight:700;color:#0D2137;margin-bottom:.2rem}
.sec-s{font-size:.89rem;color:#4A6080;margin-bottom:1.2rem}
.pred-card{background:white;border-radius:10px;padding:1.1rem 1.3rem;margin-bottom:.85rem;box-shadow:0 2px 8px rgba(4,14,28,.06)}
.pred-label{font-size:.65rem;font-weight:800;text-transform:uppercase;letter-spacing:1.6px;color:#94A3B8;margin-bottom:.3rem}
.pred-value{font-size:1.55rem;font-weight:700;color:#0D2137}
.pred-sub{font-size:.78rem;color:#64748B;margin-top:.2rem}
.bar-wrap{background:#EEF2F9;border-radius:5px;height:6px;margin:6px 0 3px}
.bar-fill{height:6px;border-radius:5px}
.verdict-p{background:#E6F5EE;color:#1B6B45;border:1px solid #A7D7BC;border-radius:8px;padding:.9rem 1.2rem;margin-bottom:.8rem}
.verdict-e{background:#FFF3E0;color:#9B5C00;border:1px solid #F5C97A;border-radius:8px;padding:.9rem 1.2rem;margin-bottom:.8rem}
.verdict-r{background:#FDE8EA;color:#9B2335;border:1px solid #F5AABA;border-radius:8px;padding:.9rem 1.2rem;margin-bottom:.8rem}
.about-card{background:white;border-radius:12px;padding:1.8rem 2rem;box-shadow:0 2px 12px rgba(4,14,28,.07);margin-bottom:1.2rem}
.sainet-badge{display:inline-flex;align-items:center;gap:.5rem;background:#0D1F35;color:#F0A500;border-radius:6px;padding:.3rem .8rem;font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:1rem}
.endpoint-table{width:100%;border-collapse:collapse;font-size:.86rem}
.endpoint-table th{background:#0D1F35;color:#F0A500;padding:.5rem .8rem;text-align:left;font-size:.72rem;text-transform:uppercase;letter-spacing:1px}
.endpoint-table td{padding:.5rem .8rem;border-bottom:1px solid #EEF2F9;color:#334155}
.endpoint-table tr:nth-child(even) td{background:#F8FAFD}
.quote-block{border-left:3px solid #F0A500;background:#FFFBF0;padding:.9rem 1.2rem;border-radius:0 8px 8px 0;font-style:italic;color:#4A3000;margin-bottom:.85rem}
.quote-attr{font-size:.75rem;font-weight:700;color:#F0A500;text-transform:uppercase;letter-spacing:1px;margin-top:.4rem}
.person-card{background:#F8FAFD;border:1px solid #D8E4F0;border-radius:8px;padding:.9rem 1.2rem;margin-bottom:.6rem;display:flex;align-items:center;gap:.8rem}
.person-name{font-size:.95rem;font-weight:700;color:#0D2137}
.person-inst{font-size:.82rem;color:#5A7299}
.role-badge{display:inline-block;padding:.2rem .6rem;border-radius:5px;font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.8px;white-space:nowrap}
.badge-pi{background:#1A3A5C;color:white}
.badge-dev{background:#F0A500;color:#040E1C}
.stButton>button{background:linear-gradient(135deg,#F0A500,#D4920A)!important;color:#040E1C!important;border:none!important;border-radius:8px!important;font-weight:700!important;font-size:.95rem!important;padding:.6rem 1.8rem!important;width:100%!important}
[data-testid="stTextInput"] input{background:#0D1F35!important;color:white!important;border:1px solid #2A4A6A!important;border-radius:8px!important;font-size:.93rem!important}
[data-testid="stTextInput"] input::placeholder{color:#6A8BAA!important}
.disclaimer{background:#F0F5FB;border:1px solid #C5D7F0;border-radius:8px;padding:.65rem 1rem;font-size:.80rem;color:#4A6080;margin-top:1.2rem}
.smiles-ex{font-family:monospace;font-size:.76rem;color:#1A3A5C;background:#EEF4FF;padding:.12rem .4rem;border-radius:4px;cursor:pointer}
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
ll = '<img src="{}" style="width:82px;height:82px;border-radius:50%;border:2.5px solid #F0A500;box-shadow:0 0 14px rgba(240,165,0,.3)">'.format(SAI_SRC) if SAI_SRC else '<div style="width:82px;height:82px;border-radius:50%;background:#1A3A5C;border:2.5px solid #F0A500"></div>'
lr = '<img src="{}" style="width:76px;height:76px;border-radius:50%;background:white;padding:4px;border:2px solid rgba(255,255,255,.2)">'.format(SSH_SRC) if SSH_SRC else '<div style="width:76px;height:76px;border-radius:50%;background:white"></div>'

st.markdown("""
<div class="sainet-header">
  <div>{ll}</div><div class="divider"></div>
  <div class="title-block">
    <h1><span style="color:white">SAI</span><span style="color:#F0A500"> BBB</span> <span style="color:rgba(255,255,255,.85);font-weight:500">Predictor</span></h1>
    <div class="tagline">&#9733; Science for Society &nbsp;|&nbsp; SSSIHL Biosciences</div>
    <div class="subtitle">CNS Drug Transport &middot; 7-Endpoint GNN Ensemble &middot; A SAI-Net Module</div>
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

def pubchem_lookup(name):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    encoded = urllib.parse.quote(name.strip())
    url = ("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
           + encoded + "/property/IsomericSMILES,IUPACName,MolecularWeight,MolecularFormula/JSON")
    try:
        with urllib.request.urlopen(url, timeout=10, context=ctx) as resp:
            import json as _j; data = _j.loads(resp.read().decode())
        p = data["PropertyTable"]["Properties"][0]
        return {"smiles": p.get("IsomericSMILES",""), "iupac": p.get("IUPACName",""),
                "mw": str(p.get("MolecularWeight","")), "formula": p.get("MolecularFormula",""),
                "cid": str(p.get("CID",""))}
    except: return None

@st.cache_resource(show_spinner="Loading SAI BBB model ensemble...")
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
            state = torch.load(ck, map_location="cpu", weights_only=False)
            sd = state.get("model_state_dict", state) if isinstance(state, dict) else state
            m = SAINetV2(); m.load_state_dict(sd, strict=True); m.eval()
            models.append(m); loaded.append(s)
        except: pass
    if not models: return None, None, "No checkpoints loaded"
    return models, loaded, None

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
    if not af or not bf: return None, "atom_feat/bond_feat not found in sainet_model"
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None: return None, "Invalid SMILES"
        x = torch.tensor([af(a) for a in mol.GetAtoms()], dtype=torch.float)
        src, dst, ea = [], [], []
        for b in mol.GetBonds():
            i, j = b.GetBeginAtomIdx(), b.GetEndAtomIdx()
            bfeat = bf(b)
            src += [i,j]; dst += [j,i]; ea += [bfeat,bfeat]
        if not src: return None, "No bonds in molecule"
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
        Draw.MolToImage(Chem.MolFromSmiles(smi), size=(260,200)).save(buf, "PNG")
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
            "TPSA": ("{:.0f} A²".format(rdMolDescriptors.CalcTPSA(mol)), rdMolDescriptors.CalcTPSA(mol) <= 90),
            "HBD":  ("{}".format(rdMolDescriptors.CalcNumHBD(mol)), rdMolDescriptors.CalcNumHBD(mol) <= 3),
            "HBA":  ("{}".format(rdMolDescriptors.CalcNumHBA(mol)), rdMolDescriptors.CalcNumHBA(mol) <= 7),
        }
    except: return {}

def make_csv(smiles, label, result, rules):
    lines = ["SAI BBB Predictor - Prediction Report",
             "Compound,{}".format(label),
             "SMILES,{}".format(smiles),
             "",
             "=== 7-ENDPOINT PREDICTIONS ===",
             "Endpoint,Type,Value,Std Dev,Interpretation"]
    interp = {
        "BBB":   lambda v: "{:.1f}% probability".format(v*100) + (" - CNS PENETRANT" if v>=0.5 else " - CNS RESTRICTED"),
        "PGP":   lambda v: "{:.1f}% probability".format(v*100) + (" - EFFLUX SUBSTRATE" if v>=0.5 else " - NOT SUBSTRATE"),
        "BCRP":  lambda v: "{:.1f}% probability".format(v*100) + (" - EFFLUX SUBSTRATE" if v>=0.5 else " - NOT SUBSTRATE"),
        "MRP1":  lambda v: "{:.1f}% probability".format(v*100) + (" - EFFLUX SUBSTRATE" if v>=0.5 else " - NOT SUBSTRATE"),
        "logBB": lambda v: "{:+.3f}".format(v) + (" - CNS penetrant (>0.30)" if v>=0.30 else " - CNS restricted (<0.30)"),
        "PAMPA": lambda v: "{:+.3f} log Pe".format(v) + (" - High permeability" if v>=-6 else " - Low permeability"),
        "Caco2": lambda v: "{:+.3f} log Papp".format(v) + (" - High absorption" if v>=-5.15 else " - Low absorption"),
    }
    types = {"BBB":"Classification","PGP":"Classification","BCRP":"Classification",
             "MRP1":"Classification","logBB":"Regression","PAMPA":"Regression","Caco2":"Regression"}
    for k,v in result.items():
        lines.append("{},{},{:.4f},{:.4f},{}".format(
            k, types[k], v["mean"], v["std"], interp[k](v["mean"])))
    lines += ["", "=== CNS DRUG-LIKENESS RULES ===", "Property,Value,Pass"]
    for prop,(val,ok) in rules.items():
        lines.append("{},{},{}".format(prop, val, "PASS" if ok else "FAIL"))
    lines += ["", "Educational/Research Use Only - SAI BBB Predictor - SSSIHL"]
    return "\n".join(lines)

tab1, tab2 = st.tabs(["Compound Search", "About SAI BBB"])

with tab1:
    st.markdown('<div class="sec-h">Predict CNS Transport Endpoints</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-s">Enter a SMILES string for direct prediction, or use a compound name to auto-fetch from PubChem. SMILES mode supports novel and virtual compounds.</div>', unsafe_allow_html=True)

    mode = st.radio("Input mode", ["SMILES (direct)", "Compound name (PubChem lookup)"],
                    horizontal=True, label_visibility="collapsed")
    smiles_input = ""; compound_label = ""; cmpd_meta = {}

    if mode == "SMILES (direct)":
        st.markdown("""<div style="font-size:.78rem;color:#64748B;margin-bottom:.4rem">
        Examples: &nbsp;
        <span class="smiles-ex">CC(=O)Oc1ccccc1C(=O)O</span> aspirin &nbsp;&nbsp;
        <span class="smiles-ex">CCOc1ccc2nc(S(N)(=O)=O)sc2c1</span> acetazolamide &nbsp;&nbsp;
        <span class="smiles-ex">CN1CCC[C@@H]1c2cccnc2</span> nicotine
        </div>""", unsafe_allow_html=True)
        c1, c2 = st.columns([5,1])
        smiles_input = c1.text_input("smiles", placeholder="Paste SMILES string here...", label_visibility="collapsed")
        run = c2.button("Predict")
        compound_label = smiles_input[:22]+"..." if len(smiles_input)>22 else smiles_input
    else:
        st.markdown("""<div style="font-size:.78rem;color:#64748B;margin-bottom:.4rem">
        Try: <b>donepezil</b> &nbsp; <b>memantine</b> &nbsp; <b>riluzole</b> &nbsp; <b>curcumin</b> &nbsp; <b>ibuprofen</b>
        </div>""", unsafe_allow_html=True)
        c1, c2 = st.columns([5,1])
        name_input = c1.text_input("name", placeholder="e.g. donepezil", label_visibility="collapsed")
        run = c2.button("Predict")
        if run and name_input.strip():
            with st.spinner("Fetching from PubChem..."):
                cmpd_meta = pubchem_lookup(name_input.strip())
            if cmpd_meta:
                smiles_input = cmpd_meta["smiles"]; compound_label = name_input.title()
            else:
                st.error("**{}** not found on PubChem. Switch to SMILES mode and paste the structure.".format(name_input))
                st.markdown('<div class="disclaimer">Get SMILES from <a href="https://pubchem.ncbi.nlm.nih.gov" target="_blank">PubChem</a> or <a href="https://www.chemspider.com" target="_blank">ChemSpider</a>.</div>', unsafe_allow_html=True)
                st.stop()
        elif run: st.warning("Enter a compound name."); st.stop()
        else: run = False

    if run and smiles_input.strip():
        if cmpd_meta:
            st.markdown("""
            <div style="background:linear-gradient(135deg,#0D1F35,#1A3A5C);border-radius:10px;
              padding:1.1rem 1.5rem;margin-bottom:1.2rem;border-left:4px solid #F0A500">
              <div style="color:#F0A500;font-size:.68rem;font-weight:800;text-transform:uppercase;letter-spacing:1.4px">Compound identified via PubChem</div>
              <div style="color:white;font-size:1.5rem;font-weight:800;margin:.2rem 0 .1rem">{name}</div>
              <div style="color:rgba(255,255,255,.6);font-size:.80rem">{iupac}</div>
              <div style="display:flex;gap:1.2rem;margin-top:.5rem;flex-wrap:wrap">
                <span style="color:rgba(255,255,255,.55);font-size:.78rem">MW <b style="color:white">{mw} Da</b></span>
                <span style="color:rgba(255,255,255,.55);font-size:.78rem">Formula <b style="color:white">{formula}</b></span>
                <span style="color:rgba(255,255,255,.55);font-size:.78rem">PubChem CID <b style="color:#F0A500">{cid}</b></span>
              </div>
            </div>""".format(name=compound_label, iupac=cmpd_meta.get("iupac",""),
                             mw=cmpd_meta.get("mw",""), formula=cmpd_meta.get("formula",""),
                             cid=cmpd_meta.get("cid","")), unsafe_allow_html=True)

        models, loaded, err = load_models()
        if err or not models:
            st.error("Model loading failed: {}".format(err or "no checkpoints")); st.stop()

        with st.spinner("Running SAI BBB prediction ({} models)...".format(len(models) if models else 0)):
            result, pred_err = predict(smiles_input.strip(), models)

        if result is None:
            st.error("Prediction failed: {}".format(pred_err)); st.stop()

        rules = cns_rules(smiles_input.strip())
        cs, cc, cr = st.columns([1.3, 2.4, 2.3])

        with cs:
            st.markdown('<div class="pred-label">2D Structure</div>', unsafe_allow_html=True)
            buf = mol_img(smiles_input.strip())
            if buf: st.image(buf, use_container_width=True)
            st.markdown('<div class="pred-label" style="margin-top:1rem">CNS Drug-likeness</div>', unsafe_allow_html=True)
            for prop,(val,ok) in rules.items():
                c_col, bg = ("#1B6B45","#E6F5EE") if ok else ("#9B2335","#FDE8EA")
                icon = "&#10003;" if ok else "&#10007;"
                st.markdown('<div style="display:flex;justify-content:space-between;padding:.38rem .7rem;background:{bg};border-radius:6px;margin-bottom:.28rem"><span style="font-size:.80rem;font-weight:600;color:{c}">{prop}</span><span style="font-size:.80rem;font-weight:700;color:{c}">{icon} {val}</span></div>'.format(bg=bg,c=c_col,prop=prop,icon=icon,val=val), unsafe_allow_html=True)

        with cc:
            st.markdown('<div class="sec-h">Classification Endpoints</div>', unsafe_allow_html=True)
            for k,lbl,tip in [
                ("BBB",  "BBB Penetration",  "P(crossing blood-brain barrier)"),
                ("PGP",  "PGP Efflux",       "P-glycoprotein efflux substrate"),
                ("BCRP", "BCRP Efflux",      "Breast cancer resistance protein"),
                ("MRP1", "MRP1 Efflux",      "Multidrug resistance protein 1"),
            ]:
                v = result[k]["mean"]; pct = v*100
                fc = "#1B6B45" if pct<40 else ("#9B5C00" if pct<70 else "#9B2335")
                st.markdown('<div class="pred-card"><div class="pred-label">{lbl}</div><div class="pred-value" style="color:{fc}">{pct:.1f}%</div><div class="bar-wrap"><div class="bar-fill" style="width:{p2:.0f}%;background:{fc}"></div></div><div class="pred-sub">{tip} &middot; &sigma;&plusmn;{std:.1f}%</div></div>'.format(lbl=lbl,fc=fc,pct=pct,p2=min(pct,100),tip=tip,std=result[k]["std"]*100), unsafe_allow_html=True)

        with cr:
            st.markdown('<div class="sec-h">Regression Endpoints</div>', unsafe_allow_html=True)
            for k,lbl,tip in [
                ("logBB","log BB (Brain/Blood)","&gt;+0.30 = CNS penetrant"),
                ("PAMPA","PAMPA log Pe",         "Passive membrane permeability"),
                ("Caco2","Caco-2 log Papp",      "Intestinal absorption"),
            ]:
                v = result[k]["mean"]
                st.markdown('<div class="pred-card"><div class="pred-label">{lbl}</div><div class="pred-value">{v:+.3f}</div><div class="pred-sub">{tip} &middot; &sigma;&plusmn;{std:.3f}</div></div>'.format(lbl=lbl,v=v,tip=tip,std=result[k]["std"]), unsafe_allow_html=True)

            bbb=result["BBB"]["mean"]; pgp=result["PGP"]["mean"]; lbb=result["logBB"]["mean"]
            if bbb>=0.5 and lbb>=0.30 and pgp<0.5:
                vc,vt,vb = "p","CNS-PENETRANT","BBB {:.0%}  logBB {:+.2f}  PGP {:.0%}".format(bbb,lbb,pgp)
            elif bbb>=0.5 and pgp>=0.5:
                vc,vt,vb = "e","EFFLUX LIMITED","BBB {:.0%}  PGP {:.0%} — efflux may limit exposure".format(bbb,pgp)
            else:
                vc,vt,vb = "r","CNS-RESTRICTED","BBB {:.0%}  logBB {:+.2f}".format(bbb,lbb)
            st.markdown('<div class="verdict-{vc}"><div style="font-size:.68rem;font-weight:800;text-transform:uppercase;letter-spacing:1.4px;margin-bottom:.3rem">SAI BBB Verdict</div><div style="font-size:1.05rem;font-weight:700">{vt}</div><div style="font-size:.80rem;margin-top:.25rem">{vb}</div></div>'.format(vc=vc,vt=vt,vb=vb), unsafe_allow_html=True)

        # ── Results Table + CSV Download ──────────────────────────────────────
        st.markdown("---")
        st.markdown('<div class="sec-h">Full Results Table</div>', unsafe_allow_html=True)
        import pandas as pd
        rows = []
        type_map = {"BBB":"Classification","PGP":"Classification","BCRP":"Classification",
                    "MRP1":"Classification","logBB":"Regression","PAMPA":"Regression","Caco2":"Regression"}
        fmt_map  = {"BBB":  lambda v: "{:.1f}%".format(v*100),
                    "PGP":  lambda v: "{:.1f}%".format(v*100),
                    "BCRP": lambda v: "{:.1f}%".format(v*100),
                    "MRP1": lambda v: "{:.1f}%".format(v*100),
                    "logBB":lambda v: "{:+.3f}".format(v),
                    "PAMPA":lambda v: "{:+.3f}".format(v),
                    "Caco2":lambda v: "{:+.3f}".format(v)}
        interp_map = {
            "BBB":  lambda v: "CNS Penetrant" if v>=0.5 else "CNS Restricted",
            "PGP":  lambda v: "Efflux Substrate" if v>=0.5 else "Not Substrate",
            "BCRP": lambda v: "Efflux Substrate" if v>=0.5 else "Not Substrate",
            "MRP1": lambda v: "Efflux Substrate" if v>=0.5 else "Not Substrate",
            "logBB":lambda v: "Penetrant (>0.30)" if v>=0.30 else "Restricted (<0.30)",
            "PAMPA":lambda v: "High Permeability" if v>=-6 else "Low Permeability",
            "Caco2":lambda v: "High Absorption" if v>=-5.15 else "Low Absorption",
        }
        for k,v in result.items():
            rows.append({"Endpoint": k, "Type": type_map[k],
                         "Predicted Value": fmt_map[k](v["mean"]),
                         "Std Dev (±)": "{:.4f}".format(v["std"]),
                         "Interpretation": interp_map[k](v["mean"])})
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        csv_str = make_csv(smiles_input.strip(), compound_label, result, rules)
        st.download_button("Download Report (CSV)",
            data=csv_str, mime="text/csv",
            file_name="saibbb_{}.csv".format(compound_label.lower().replace(" ","_").replace("/","")))
        st.markdown('<div class="disclaimer"><b>Educational/Research Use Only</b> — Predictions are computational estimates. Not for clinical decision making.</div>', unsafe_allow_html=True)

    elif run:
        st.warning("Please enter a SMILES string or compound name.")

with tab2:
    # SAI-Net connection banner
    st.markdown("""<div class="about-card">
      <div class="sainet-badge">&#9670; SAI-Net Framework Module</div>
      <div style="font-size:1.55rem;font-weight:800;color:#0D2137;margin-bottom:.4rem">
        <span style="background:#0D2137;color:white;padding:0 .3rem;border-radius:3px">SAI</span>
        <span style="color:#F0A500"> BBB</span>
        <span style="color:#0D2137;font-weight:500"> Predictor</span>
      </div>
      <div style="background:#F0A500;height:3px;width:60px;border-radius:2px;margin-bottom:1rem"></div>
      <p style="color:#334155;font-size:.91rem;line-height:1.8;margin-bottom:.6rem">
        SAI BBB Predictor is a translational web module of the
        <b style="color:#0D2137">SAI-Net (Structure-Activity Intelligence Network)</b> framework —
        a computational neuropharmacology platform for multiomics-integrated drug discovery
        across neurodegenerative disease spectra including ALS, Alzheimer&apos;s, Parkinson&apos;s,
        and Huntington&apos;s disease.
      </p>
      <p style="color:#334155;font-size:.91rem;line-height:1.8">
        This module specifically addresses the <b>blood-brain barrier bottleneck</b> in CNS drug development —
        one of the highest attrition points in neurotherapeutic pipelines — by providing simultaneous
        prediction of 7 transport endpoints using a multitask graph attention network ensemble.
      </p>
    </div>""", unsafe_allow_html=True)

    # Innovation / NAR fit
    st.markdown("""<div class="about-card">
      <div style="font-size:1.05rem;font-weight:700;color:#0D2137;margin-bottom:1rem">Why SAI BBB? Innovation &amp; Design</div>
      <table class="endpoint-table">
        <tr><th>Endpoint</th><th>Type</th><th>Clinical Relevance</th><th>Threshold</th></tr>
        <tr><td><b>BBB Penetration</b></td><td>Classification</td><td>Primary CNS exposure predictor</td><td>P &ge; 0.50</td></tr>
        <tr><td><b>PGP Efflux</b></td><td>Classification</td><td>P-gp limits brain accumulation</td><td>P &lt; 0.50 desired</td></tr>
        <tr><td><b>BCRP Efflux</b></td><td>Classification</td><td>BCRP co-expressed at BBB</td><td>P &lt; 0.50 desired</td></tr>
        <tr><td><b>MRP1 Efflux</b></td><td>Classification</td><td>Active efflux at choroid plexus</td><td>P &lt; 0.50 desired</td></tr>
        <tr><td><b>log BB</b></td><td>Regression</td><td>Quantitative brain/blood ratio</td><td>&gt; +0.30 penetrant</td></tr>
        <tr><td><b>PAMPA log Pe</b></td><td>Regression</td><td>Passive transcellular permeability</td><td>&gt; &minus;6.0 high</td></tr>
        <tr><td><b>Caco-2 log Papp</b></td><td>Regression</td><td>Intestinal/paracellular absorption</td><td>&gt; &minus;5.15 high</td></tr>
      </table>
      <div style="background:#EEF4FF;border-radius:8px;padding:.9rem 1.1rem;margin-top:1rem;border-left:3px solid #1A3A5C">
        <b style="color:#1A3A5C;font-size:.85rem">Key innovation:</b>
        <span style="color:#334155;font-size:.85rem"> Simultaneous multitask GNN prediction with 5-seed ensemble uncertainty quantification —
        enabling scientists to assess not just a single endpoint, but the complete CNS transport liability profile
        of any compound in a single forward pass from SMILES input.</span>
      </div>
    </div>""", unsafe_allow_html=True)

    # Science for Society
    st.markdown("""<div class="about-card">
      <div style="font-size:1.05rem;font-weight:700;color:#0D2137;margin-bottom:.6rem">Science for Society &mdash; 100 Years of Selfless Service</div>
      <div class="quote-block">&ldquo;Let the world achieve the glory of becoming a family &mdash; through Love.&rdquo;
        <div class="quote-attr">&mdash; Bhagawan Sri Sathya Sai Baba</div></div>
      <div class="quote-block">&ldquo;True knowledge is that which makes man work for the welfare of humanity.&rdquo;
        <div class="quote-attr">&mdash; Bhagawan Sri Sathya Sai Baba</div></div>
      <p style="color:#334155;font-size:.88rem;line-height:1.75">
        This tool is dedicated to the centenary of selfless service and unconditional love of
        <b>Bhagawan Sri Sathya Sai Baba (1926&ndash;2011)</b>. It is offered freely to the global
        scientific community in that spirit.</p>
    </div>""", unsafe_allow_html=True)

    # Team + target publication
    st.markdown("""<div class="about-card">
      <div style="font-size:1.05rem;font-weight:700;color:#0D2137;margin-bottom:1rem">Research Team</div>
      <div class="person-card">
        <span class="role-badge badge-pi">Principal Investigator</span>
        <div><div class="person-name">Prof. Venketesh Sivaramakrishnan</div>
        <div class="person-inst">Department of Biosciences &mdash; Sri Sathya Sai Institute of Higher Learning, Puttaparthi</div></div>
      </div>
      <div class="person-card">
        <span class="role-badge badge-dev">Developer</span>
        <div><div class="person-name">Krishnasalini Gunanathan</div>
        <div class="person-inst">Doctoral Research Scholar, Biosciences &mdash; Sri Sathya Sai Institute of Higher Learning</div></div>
      </div>
      <div style="background:#EEF4FF;border-radius:8px;padding:.8rem 1.1rem;margin-top:.8rem;border-left:3px solid #F0A500">
        <b style="color:#1A3A5C;font-size:.85rem">Target Publication: </b>
        <span style="color:#334155;font-size:.85rem">Nucleic Acids Research &mdash; Web Server Issue 2026</span>
      </div>
    </div>
    <div class="disclaimer"><b>Educational/Research Use Only</b> &mdash; This tool is not intended as medical or clinical advice. Consult a qualified professional before making any decisions based on these predictions.</div>
    """, unsafe_allow_html=True)
