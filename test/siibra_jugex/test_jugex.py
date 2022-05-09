from unittest.mock import patch, Mock
import pytest
from siibra import parcellations, MapType
from siibra_jugex import jugex

@patch('siibra.get_features')
def test_thresholding(mock_get_features: Mock):
    mock_get_features.return_value = []

    p = parcellations['2.9']
    r1 = 'fp1 left'
    gene_names = ["MAOA", "TAC1"]
    
    analysis = jugex.DifferentialGeneExpression(p, gene_names)
    threshold=0.2
    analysis.define_roi1(r1, maptype=MapType.CONTINUOUS, threshold=threshold)

    region = p.decode_region(r1)
    for gene_name in gene_names:
        mock_get_features.assert_any_call(region, "gene", gene=gene_name, maptype=MapType.CONTINUOUS, threshold_continuous=threshold)
