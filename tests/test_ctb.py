import random

import pytest

from check_the_box import create_entity_and_responses
from check_the_box.app import create_app
from check_the_box.ctb import style_green

NUM_PROBLEMS = 2000  # enough random draws to hit every country, entity type, and branch


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client()


def test_each_problem_has_four_answers_and_exactly_one_correct():
    random.seed(0)
    for _ in range(NUM_PROBLEMS):
        entity, responses = create_entity_and_responses()
        assert len(responses) == 4, entity
        num_correct = sum(style_green in response for response in responses.values())
        assert num_correct == 1, entity


def test_problem_text_is_complete():
    random.seed(1)
    for _ in range(NUM_PROBLEMS):
        entity, _ = create_entity_and_responses()
        for value in (entity.name, entity.type_long_form, entity.type_short_form, entity.country_or_state):
            assert value, entity
        assert 'None' not in entity.problem_basic_question, entity


def test_entities_that_cannot_have_one_member_are_multi_member():
    random.seed(2)
    for _ in range(NUM_PROBLEMS):
        entity, _ = create_entity_and_responses()
        if not entity.per_se and entity.type_short_form in {'LLP', 'GP', 'LP'}:
            assert not entity.single_member, entity


def test_page_renders(client):
    response = client.get('/resources/check_the_box')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Practice Problems on Check-the-Box Rules' in html
    assert html.count('type="radio" name="answer"') == 4
    assert '<title>Check-the-Box Practice Problems</title>' in html


def test_home_redirects_to_problems(client):
    response = client.get('/')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/resources/check_the_box')
