import ibis
import pytest
from pandas.testing import assert_frame_equal

from dagster_dunks.pipelines.data_processing.nodes import prepare_results_by_team


@pytest.fixture
def results(request):
    return ibis.memtable(
        {
            "Season": [2003],
            "DayNum": [10],
            "WTeamID": [1104],
            "WScore": [68],
            "LTeamID": [1328],
            "LScore": [62],
            "WLoc": [request.param],
            "NumOT": [0],
        }
    )


@pytest.mark.parametrize(
    ("results", "location"),
    [("H", ["H", "A"]), ("A", ["A", "H"]), ("N", ["N", "N"])],
    indirect=["results"],
)
def test_prepare_results_by_team(results, location):
    got = prepare_results_by_team(results)
    expected = ibis.memtable(
        {
            "Season": [2003, 2003],
            "DayNum": [10, 10],
            "TeamID": [1104, 1328],
            "Score": [68, 62],
            "opponent_TeamID": [1328, 1104],
            "opponent_Score": [62, 68],
            "location": location,
            "NumOT": [0, 0],
        }
    )
    assert_frame_equal(got.execute(), expected.execute())
