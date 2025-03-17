import ibis
import pytest
from pandas.testing import assert_frame_equal

from dagster_dunks.pipelines.data_processing.nodes import prepare_results_by_team


@pytest.fixture
def results():
    return ibis.memtable(
        {
            "Season": [2003],
            "DayNum": [10],
            "WTeamID": [1104],
            "WScore": [68],
            "LTeamID": [1328],
            "LScore": [62],
            "WLoc": ["N"],
            "NumOT": [0],
        }
    )


def test_prepare_results_by_team(results):
    got = prepare_results_by_team(results)
    expected = ibis.memtable(
        {
            "Season": [2003, 2003],
            "DayNum": [10, 10],
            "TeamID": [1104, 1328],
            "Score": [68, 62],
            "opponent_TeamID": [1328, 1104],
            "opponent_Score": [62, 68],
            "location": ["N", "N"],
            "NumOT": [0, 0],
        }
    )
    assert_frame_equal(got.execute(), expected.execute())
