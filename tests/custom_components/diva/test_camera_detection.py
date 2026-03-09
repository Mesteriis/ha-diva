import numpy as np

from custom_components.diva.pet import BowlArea, analyze_frame


def test_camera_analysis_detects_bowl_motion_and_empty_state() -> None:
    previous = np.full((100, 100, 3), 255, dtype=np.uint8)
    current = previous.copy()
    current[10:30, 10:30] = 0

    analysis = analyze_frame(
        current,
        previous,
        BowlArea(10, 10, 20, 20),
        None,
        food_reference=previous,
    )

    assert analysis.food_interaction is True
    assert analysis.food_empty is True
    assert analysis.food_motion_score > 0
