from fastapi.testclient import TestClient

from siibra_jugex_http.main import app

client = TestClient(app)

def test_getting_notebook():
    from urllib.parse import urlencode
    import random, string

    def get_random_string():
        return "".join(random.choices(string.ascii_uppercase, k=8))

    roi_1 = get_random_string()
    roi_2 = get_random_string()
    genes = [ get_random_string(), get_random_string() ]
    perm = round(random.random() * 1000)
    threshold = random.random()
    encoded_url = urlencode({
        'parcellation_id': '2.9',
        'roi_1': roi_1,
        'roi_2': roi_2,
        'comma_delimited_genes': ",".join(genes),
        'permutations': perm,
        'threshold': threshold,
    })
    resp = client.get(f"/notebook/download?{encoded_url}")
    
    resp.raise_for_status()
    text = resp.text
    assert roi_1 in text
    assert roi_2 in text
    assert all(
        gene in text for gene in genes
    )
    assert f'permutations = {perm}' in text
    assert f"threshold = {threshold}" in text
