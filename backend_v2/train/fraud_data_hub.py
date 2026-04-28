import pandas as pd
import numpy as np
import torch
from pathlib import Path

class FraudDataHub:
    """
    Central hub for managing multi-source fraud data:
    1. Elliptic (Graph/Network)
    2. PaySim (Mobile Transaction Flow)
    3. IEEE-CIS (Identity/Device Fingerprint)
    """
    def __init__(self, data_root: str):
        self.data_root = Path(data_root)
        
    def load_elliptic(self):
        """
        Loads the Elliptic Bitcoin dataset for GNN training.
        Returns: x, edge_index, labels
        """
        base = self.data_root / "elliptic_bitcoin_dataset"
        features = pd.read_csv(base / "elliptic_txs_features.csv", header=None)
        edgelist = pd.read_csv(base / "elliptic_txs_edgelist.csv")
        classes = pd.read_csv(base / "elliptic_txs_classes.csv")
        
        # 1. Process Nodes & Features
        # First column is txId
        tx_ids = features[0].values
        x = features.iloc[:, 1:].values.astype(np.float32)
        
        # 2. Process Edges
        # Create a mapping from txId to node index
        id_map = {tid: i for i, tid in enumerate(tx_ids)}
        edgelist['txId1'] = edgelist['txId1'].map(id_map)
        edgelist['txId2'] = edgelist['txId2'].map(id_map)
        edge_index = torch.tensor(edgelist[['txId1', 'txId2']].values.T, dtype=torch.long)
        
        # 3. Process Labels
        # 1=illicit, 2=licit, unknown='unknown'
        classes['class'] = classes['class'].map({'1': 1, '2': 0, 'unknown': -1})
        y = torch.tensor(classes['class'].values, dtype=torch.long)
        
        return torch.tensor(x), edge_index, y

    def load_paysim(self):
        """
        Loads the PaySim dataset for behavioral flow detection.
        """
        path = self.data_root / "PS_20174392719_1491204439457_log.csv"
        if not path.exists():
            return None
        df = pd.read_csv(path)
        # Basic preprocessing
        df = pd.get_dummies(df, columns=['type'])
        return df

    def load_ieee_cis(self):
        """
        Loads and joins IEEE-CIS Transaction and Identity datasets.
        """
        trans_path = self.data_root / "train_transaction.csv"
        ident_path = self.data_root / "train_identity.csv"
        
        if not trans_path.exists():
            return None
            
        train_trans = pd.read_csv(trans_path)
        train_ident = pd.read_csv(ident_path) if ident_path.exists() else None
        
        if train_ident is not None:
            df = pd.merge(train_trans, train_ident, on='TransactionID', how='left')
        else:
            df = train_trans
            
        return df

if __name__ == "__main__":
    hub = FraudDataHub(r"c:\Users\rutur\OneDrive\Desktop\jotex\Dataset\fraud")
    print("[hub] Initialized Data Hub")
    # Uncomment to test loading (caution: large files)
    # x, edges, y = hub.load_elliptic()
    # print(f"Elliptic loaded: {x.shape} nodes")
