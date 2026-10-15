"""Build the MaleCNS v1.0 neuron graph from the official flat-connectome files.

Filter (stated, not hidden): keep bodies that carry a `superclass` annotation.
That yields 166,700 neurons, which matches the published cell count.

Sign policy (an assumption, not data): consensus_nt acetylcholine -> +1,
gaba/glutamate -> -1, everything else -> 0.  Chosen to match the independent
mps-malecns-model implementation so the build can be cross-checked against it.

Edge weight (an assumption, not data):
    w[post, pre] = contacts(pre->post) / total_retained_input_contacts(post)
                   * sign(pre)
Not in physiological conductance units.
"""
import numpy as np
import pyarrow.feather as feather
from scipy import sparse

SRC = "<DATA_ROOT>/cache/substrates/male-cns-v1.0/source/"
OUT = "<DATA_ROOT>/malecns_graph.npz"

ANN = SRC + "body-annotations-male-cns-v1.0-minconf-0.5.feather"
NT = SRC + "body-neurotransmitters-male-cns-v1.0.feather"
CONN = SRC + "connectome-weights-male-cns-v1.0-minconf-0.5.feather"

SIGN = {"acetylcholine": 1.0, "gaba": -1.0, "glutamate": -1.0}


def main():
    ann = feather.read_table(ANN, columns=["bodyId", "superclass", "type", "class"],
                             memory_map=True)
    body = ann.column("bodyId").to_numpy().astype(np.int64)
    sclass = np.array(ann.column("superclass").to_pylist(), dtype=object)
    types = np.array(ann.column("type").to_pylist(), dtype=object)

    has_sc = sclass != None  # noqa: E711 - object array, `is not None` won't vectorize
    keep_body = body[has_sc]
    keep_type = types[has_sc]
    keep_sc = sclass[has_sc]
    order = np.argsort(keep_body, kind="stable")
    keep_body, keep_type, keep_sc = keep_body[order], keep_type[order], keep_sc[order]
    # annotations may repeat a bodyId; collapse to first occurrence
    uniq, first = np.unique(keep_body, return_index=True)
    keep_body, keep_type, keep_sc = uniq, keep_type[first], keep_sc[first]
    n = len(keep_body)
    print(f"neurons kept (has superclass): {n}", flush=True)

    nt = feather.read_table(NT, columns=["body", "consensus_nt"], memory_map=True)
    nt_body = nt.column("body").to_numpy().astype(np.int64)
    nt_val = np.array(nt.column("consensus_nt").to_pylist(), dtype=object)
    sign_by_body = np.zeros(len(nt_body), dtype=np.float32)
    for name, s in SIGN.items():
        sign_by_body[nt_val == name] = s
    pos = np.searchsorted(nt_body, keep_body) if np.all(np.diff(nt_body) >= 0) else None
    if pos is None:
        o = np.argsort(nt_body, kind="stable")
        nt_body, sign_by_body = nt_body[o], sign_by_body[o]
        pos = np.searchsorted(nt_body, keep_body)
    pos = np.clip(pos, 0, len(nt_body) - 1)
    sign = np.where(nt_body[pos] == keep_body, sign_by_body[pos], 0.0).astype(np.float32)
    n_zero_sign = int((sign == 0).sum())
    print(f"neurons with sign 0 (nt not ACh/GABA/Glu or missing): {n_zero_sign}", flush=True)

    t = feather.read_table(CONN, memory_map=True)
    pre = t.column("body_pre").to_numpy().astype(np.int64)
    post = t.column("body_post").to_numpy().astype(np.int64)
    contacts = t.column("weight").to_numpy().astype(np.float32)
    del t

    ipre = np.searchsorted(keep_body, pre)
    np.clip(ipre, 0, n - 1, out=ipre)
    ok_pre = keep_body[ipre] == pre
    ipost = np.searchsorted(keep_body, post)
    np.clip(ipost, 0, n - 1, out=ipost)
    ok_post = keep_body[ipost] == post
    m = ok_pre & ok_post
    ipre, ipost, contacts = ipre[m], ipost[m], contacts[m]
    print(f"directed connections: {len(ipre)}", flush=True)
    print(f"synaptic contacts:    {int(contacts.sum())}", flush=True)

    in_total = np.bincount(ipost, weights=contacts, minlength=n).astype(np.float32)
    in_total[in_total == 0] = 1.0
    w = (contacts / in_total[ipost]) * sign[ipre]
    n_zero_w = int((w == 0).sum())
    print(f"connections with zero dynamic weight: {n_zero_w}", flush=True)

    W = sparse.csr_matrix((w, (ipost, ipre)), shape=(n, n), dtype=np.float32)
    np.savez_compressed(
        OUT, data=W.data, indices=W.indices, indptr=W.indptr, shape=np.array(W.shape),
        body_ids=keep_body, sign=sign,
        types=np.array([x if x is not None else "" for x in keep_type], dtype=object),
        superclass=np.array([x if x is not None else "" for x in keep_sc], dtype=object),
    )
    print(f"saved {OUT}  nnz={W.nnz}", flush=True)


if __name__ == "__main__":
    main()
