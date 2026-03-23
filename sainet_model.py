#!/usr/bin/env python3
"""SAI-Net v2: Multitask GNN for BBB/CNS-ADMET (12 tasks)"""

import sys, os, json, warnings, random, time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader
from torch_geometric.nn import GATv2Conv, global_mean_pool, global_add_pool
from sklearn.metrics import roc_auc_score, matthews_corrcoef, balanced_accuracy_score
from scipy.stats import pearsonr
from rdkit import Chem
warnings.filterwarnings("ignore")

# ════════════════════════════════════════════════════════════
# CONSTANTS
# ════════════════════════════════════════════════════════════
TASKS     = ["BBB","logBB","PGP","BCRP","MRP1","PAMPA","Caco2","LogP","PPBR","CYP3A4","CYP2C19","CYP1A2"]
TRAINED_TASKS = ["BBB","logBB","PGP","BCRP","MRP1","PAMPA","Caco2"]  # heads present in checkpoints


N_TASKS   = len(TASKS)
TASK_IDX  = {t: i for i, t in enumerate(TASKS)}
CLS_TASKS = {"BBB","PGP","BCRP","MRP1","CYP3A4","CYP2C19","CYP1A2"}
REG_TASKS = {"logBB","PAMPA","Caco2","LogP","PPBR"}
TASK_W = torch.tensor([
    2.0,  # BBB     — strong anchor
    3.0,  # logBB   — data-limited regression
    2.0,  # PGP     — keep
    1.5,  # BCRP    — near SOTA
    4.0,  # MRP1    — severely data-limited
    3.0,  # PAMPA   — data-limited + new data added
    2.5,  # Caco2   — data-limited + new data added
    1.5,  # LogP    — was 0.4 → fixed
    3.0,  # PPBR    — was 0.3 → fixed + new data added
    1.2,  # CYP3A4  — was 0.05 → fixed
    1.2,  # CYP2C19 — was 0.05 → fixed
    1.0,  # CYP1A2  — was 0.05 → fixed
])
DEVICE    = "cuda" if torch.cuda.is_available() else "cpu"
# ════════════════════════════════════════════════════════════
# FEATURIZATION
# ════════════════════════════════════════════════════════════
ATOM_TYPES  = ["C","N","O","S","F","Cl","Br","I","P","B","Si","Se","other"]
DEGREES     = [0,1,2,3,4,5]
H_COUNTS    = [0,1,2,3,4]
CHARGES     = [-2,-1,0,1,2]
HYBRID      = [Chem.rdchem.HybridizationType.SP,
               Chem.rdchem.HybridizationType.SP2,
               Chem.rdchem.HybridizationType.SP3,
               Chem.rdchem.HybridizationType.SP3D,
               Chem.rdchem.HybridizationType.SP3D2]
BOND_TYPES  = [Chem.rdchem.BondType.SINGLE, Chem.rdchem.BondType.DOUBLE,
               Chem.rdchem.BondType.TRIPLE, Chem.rdchem.BondType.AROMATIC]
STEREO      = [Chem.rdchem.BondStereo.STEREONONE, Chem.rdchem.BondStereo.STEREOANY,
               Chem.rdchem.BondStereo.STEREOZ,    Chem.rdchem.BondStereo.STEREOE]

def ohe(val, choices, other=True):
    v = [int(val == c) for c in choices]
    if other: v.append(int(val not in choices))
    return v

def atom_feat(a):
    return (ohe(a.GetSymbol(), ATOM_TYPES) +
            ohe(a.GetDegree(), DEGREES) +
            ohe(a.GetTotalNumHs(), H_COUNTS) +
            ohe(a.GetFormalCharge(), CHARGES) +
            ohe(a.GetHybridization(), HYBRID) +
            [int(a.GetIsAromatic()), int(a.IsInRing())])

def bond_feat(b):
    return (ohe(b.GetBondType(), BOND_TYPES, other=False) +
            [int(b.GetIsConjugated()), int(b.IsInRing())] +
            ohe(b.GetStereo(), STEREO, other=False))

_dummy_mol  = Chem.MolFromSmiles("CC")
NODE_DIM    = len(atom_feat(_dummy_mol.GetAtomWithIdx(0)))
EDGE_DIM    = len(bond_feat(_dummy_mol.GetBondWithIdx(0)))

def smiles_to_data(smi, labels=None, mask=None):
    mol = Chem.MolFromSmiles(str(smi))
    if mol is None: return None
    x = torch.tensor([atom_feat(a) for a in mol.GetAtoms()], dtype=torch.float)
    src, dst, ea = [], [], []
    for b in mol.GetBonds():
        i, j = b.GetBeginAtomIdx(), b.GetEndAtomIdx()
        bf = bond_feat(b)
        src += [i, j]; dst += [j, i]; ea += [bf, bf]
    if not src: return None
    d = Data(x=x,
             edge_index=torch.tensor([src, dst], dtype=torch.long),
             edge_attr=torch.tensor(ea, dtype=torch.float))
    if labels is not None:
        d.y    = torch.tensor(labels, dtype=torch.float)
        d.mask = torch.tensor(mask,   dtype=torch.bool)
    return d

# ════════════════════════════════════════════════════════════
# DATASET
# ════════════════════════════════════════════════════════════
class MultiTaskDataset(torch.utils.data.Dataset):
    def __init__(self, csv_path):
        df  = pd.read_csv(csv_path)
        df  = df[df["SMILES"].notna() & (df["SMILES"].str.strip() != "")]
        self.items = []
        skipped = 0
        for _, row in df.iterrows():
            labels, mask = [], []
            for t in TASKS:
                v = row.get(t, float("nan"))
                if pd.notna(v):
                    labels.append(float(v)); mask.append(True)
                else:
                    labels.append(0.0);      mask.append(False)
            if not any(mask): skipped += 1; continue
            d = smiles_to_data(row["SMILES"], labels, mask)
            if d is not None: self.items.append(d)
            else: skipped += 1
        print(f"  {os.path.basename(csv_path)}: loaded={len(self.items):,} skipped={skipped}")
    def __len__(self):         return len(self.items)
    def __getitem__(self, i):  return self.items[i]

# ════════════════════════════════════════════════════════════
# MODEL
# ════════════════════════════════════════════════════════════
class SAINetV2(nn.Module):
    def __init__(self, node_dim=NODE_DIM, edge_dim=EDGE_DIM,
                 hidden=256, n_layers=6, heads=4, dropout=0.15):
        super().__init__()
        self.node_emb = nn.Linear(node_dim, hidden)
        self.edge_emb = nn.Linear(edge_dim, hidden)
        self.convs = nn.ModuleList([
            GATv2Conv(hidden, hidden // heads, heads=heads,
                      edge_dim=hidden, add_self_loops=False)
            for _ in range(n_layers)])
        self.norms   = nn.ModuleList([nn.LayerNorm(hidden) for _ in range(n_layers)])
        self.drop    = nn.Dropout(dropout)
        self.mol_fc  = nn.Sequential(
            nn.Linear(hidden * 2, hidden), nn.SiLU(),
            nn.Dropout(dropout),          nn.Linear(hidden, hidden))
        self.task_heads = nn.ModuleDict({
            t: nn.Sequential(
                nn.Linear(hidden, 128), nn.SiLU(), nn.Dropout(dropout),
                nn.Linear(128, 64),    nn.SiLU(),
                nn.Linear(64, 1))
            for t in TASKS})

    def encode(self, x, edge_index, edge_attr, batch):
        x = self.node_emb(x)
        e = self.edge_emb(edge_attr)
        for conv, norm in zip(self.convs, self.norms):
            x = norm(x + self.drop(conv(x, edge_index, e)))
        g = torch.cat([global_mean_pool(x, batch),
                       global_add_pool(x, batch)], dim=-1)
        return self.mol_fc(g)

    def forward(self, data):
        z   = self.encode(data.x, data.edge_index, data.edge_attr, data.batch)
        out = torch.stack([self.task_heads[t](z).squeeze(-1) for t in TASKS], dim=1)
        return out  # [B, 12] — logits for cls, raw for reg

# ════════════════════════════════════════════════════════════
# LOSS
# ════════════════════════════════════════════════════════════
def multitask_loss(pred, y, mask):
    w = TASK_W.to(pred.device)
    total = torch.zeros(1, device=pred.device, requires_grad=False)
    task_losses = {}
    for i, t in enumerate(TASKS):
        m = mask[:, i]
        if m.sum() == 0: continue
        p, gt = pred[m, i], y[m, i]
        loss = (F.binary_cross_entropy_with_logits(p, gt)
                if t in CLS_TASKS else F.huber_loss(p, gt, delta=1.0))
        total = total + w[i] * loss
        task_losses[t] = round(loss.item(), 4)
    return total.squeeze(), task_losses

# ════════════════════════════════════════════════════════════
# EVALUATION
# ════════════════════════════════════════════════════════════
def evaluate(model, loader):
    model.eval()
    preds = [[] for _ in TASKS]
    trues = [[] for _ in TASKS]
    with torch.no_grad():
        for b in loader:
            b   = b.to(DEVICE)
            out = model(b)
            y   = b.y.view(-1, N_TASKS)
            msk = b.mask.view(-1, N_TASKS)
            for i in range(N_TASKS):
                m = msk[:, i]
                if m.sum() == 0: continue
                preds[i].extend(out[m, i].cpu().tolist())
                trues[i].extend(y[m, i].cpu().tolist())
    results = {}
    for i, t in enumerate(TASKS):
        if len(trues[i]) < 4: continue
        p, gt = np.array(preds[i]), np.array(trues[i])
        if t in CLS_TASKS:
            ps = torch.sigmoid(torch.tensor(p)).numpy()
            try:
                auc = roc_auc_score(gt, ps)
                bm, bt = -1, 0.5
                for th in np.arange(0.1, 0.9, 0.02):
                    mc = matthews_corrcoef(gt, (ps >= th).astype(int))
                    if mc > bm: bm, bt = mc, th
                ba = balanced_accuracy_score(gt, (ps >= bt).astype(int))
                results[t] = {"n": len(gt), "AUC": round(auc, 4),
                              "MCC": round(bm, 4), "BA": round(ba, 4)}
            except Exception as e:
                results[t] = {"n": len(gt), "error": str(e)}
        else:
            try:
                r, _ = pearsonr(p, gt)
                rmse = float(np.sqrt(np.mean((p - gt) ** 2)))
                results[t] = {"n": len(gt), "r": round(r, 4), "RMSE": round(rmse, 4)}
            except Exception as e:
                results[t] = {"n": len(gt), "error": str(e)}
    return results

# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SAI-Net v2 Multitask Training")
    parser.add_argument("--data_dir", default="efflux_v2/2026_02_24/data/multitask_v1")
    parser.add_argument("--out_dir",  default="efflux_v2/multitask_v2/checkpoints")
    parser.add_argument("--epochs",   type=int,   default=150)
    parser.add_argument("--batch",    type=int,   default=256)
    parser.add_argument("--lr",       type=float, default=3e-4)
    parser.add_argument("--hidden",   type=int,   default=256)
    parser.add_argument("--layers",   type=int,   default=6)
    parser.add_argument("--patience", type=int,   default=20)
    parser.add_argument("--seed",     type=int,   default=42)
    args = parser.parse_args()

    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)

    print("=" * 60)
    print(f"SAI-Net v2 Multitask | device={DEVICE} | hidden={args.hidden} | layers={args.layers}")
    print(f"Tasks: {TASKS}")
    print("=" * 60)

    print("\nLoading datasets...")
    train_ds = MultiTaskDataset(f"{args.data_dir}/multitask_train_norm.csv")
    val_ds   = MultiTaskDataset(f"{args.data_dir}/multitask_val_norm.csv")
    test_ds  = MultiTaskDataset(f"{args.data_dir}/multitask_test_norm.csv")

    train_loader = DataLoader(train_ds, batch_size=args.batch, shuffle=True,  num_workers=2)
    val_loader   = DataLoader(val_ds,   batch_size=args.batch, shuffle=False, num_workers=2)
    test_loader  = DataLoader(test_ds,  batch_size=args.batch, shuffle=False, num_workers=2)

    model = SAINetV2(hidden=args.hidden, n_layers=args.layers).to(DEVICE)
    n_p   = sum(p.numel() for p in model.parameters())
    print(f"\nModel parameters: {n_p:,}")
    print(f"NODE_DIM={NODE_DIM} | EDGE_DIM={EDGE_DIM}")

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    best_auc, patience_ctr, history = 0.0, 0, []

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        model.train()
        ep_loss = 0.0
        for batch in train_loader:
            batch = batch.to(DEVICE)
            optimizer.zero_grad()
            pred  = model(batch)
            y     = batch.y.view(-1, N_TASKS)
            mask  = batch.mask.view(-1, N_TASKS)
            loss, _ = multitask_loss(pred, y, mask)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            ep_loss += loss.item()
        scheduler.step()

        # Validation loss
        model.eval()
        vl = 0.0
        with torch.no_grad():
            for batch in val_loader:
                batch = batch.to(DEVICE)
                pred  = model(batch)
                y     = batch.y.view(-1, N_TASKS)
                mask  = batch.mask.view(-1, N_TASKS)
                loss, _ = multitask_loss(pred, y, mask)
                vl += loss.item()
        vl /= max(len(val_loader), 1)

        vr_q   = evaluate(model, val_loader)
        cur_auc = vr_q.get("BBB", {}).get("AUC", 0.0) or 0.0
        if cur_auc > best_auc:
            best_auc = cur_auc; patience_ctr = 0
            torch.save(model.state_dict(), f"{args.out_dir}/best_model.pt")
        else:
            patience_ctr += 1

        elapsed = time.time() - t0
        if epoch % 5 == 0 or epoch == 1:
            vr = evaluate(model, val_loader)
            bbb  = vr.get("BBB",  {}).get("AUC",  "?")
            pgp  = vr.get("PGP",  {}).get("AUC",  "?")
            bcrp = vr.get("BCRP", {}).get("AUC",  "?")
            lb_r = vr.get("logBB",{}).get("r",    "?")
            print(f"  Ep {epoch:3d} | tr={ep_loss/len(train_loader):.4f} val={vl:.4f} "
                  f"| BBB={bbb} PGP={pgp} BCRP={bcrp} logBB_r={lb_r} "
                  f"| {elapsed:.0f}s | p={patience_ctr}/{args.patience}")

        history.append({"epoch": epoch,
                        "train_loss": round(ep_loss / len(train_loader), 5),
                        "val_loss":   round(vl, 5)})
        if patience_ctr >= args.patience:
            print(f"\nEarly stopping at epoch {epoch}")
            break

    # Final test evaluation
    print("\n" + "=" * 60)
    print("TEST SET RESULTS (best checkpoint)")
    print("=" * 60)
    model.load_state_dict(torch.load(f"{args.out_dir}/best_model.pt", map_location=DEVICE))
    test_res = evaluate(model, test_loader)
    for t, res in test_res.items():
        print(f"  {t:<12} {res}")

    with open(f"{args.out_dir}/test_results.json",   "w") as f: json.dump(test_res, f, indent=2)
    with open(f"{args.out_dir}/training_history.json","w") as f: json.dump(history, f, indent=2)
    print(f"\nAll outputs saved to {args.out_dir}/")
