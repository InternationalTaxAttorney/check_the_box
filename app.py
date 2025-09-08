import json
import random
from dataclasses import dataclass

from flask import Flask, render_template

app = Flask(__name__)

# entity names are based on animal names
with open('json/animalsbycountry.json', 'r', encoding='utf-8') as f:
    animals_by_country = json.load(f)

# person names are used for owners of entities
with open('json/names.json', 'r', encoding='utf-8') as f:
    names = json.load(f)

# a list of the 50 states
with open('json/states.json', 'r', encoding='utf-8') as f:
    states = json.load(f)

# names of per se, elig with ltd liab, elig with unltd liab by country
with open('json/country_data.json', 'r', encoding='utf-8') as f:
    country_data = json.load(f)

# names of per se, elig with ltd liab, elig with unltd liab for US only
with open('json/us_data.json', 'r', encoding='utf-8') as f:
    US_data = json.load(f)


@dataclass(slots=True)
class BusinessEntity:
    foreign: bool | None = None
    per_se: bool | None = None
    all_mems_ltd_liab: bool | None = None
    single_member: bool | None = None
    default: bool | None = None
    elect: bool | None = None  # opposite of default
    name: str | None = None
    type_long_form: str | None = None
    type_short_form: str | None = None  # full name of suffix
    country_or_state: str | None = None  # only if not US
    language: str | None = None
    liability_language_general: str | None = None
    liability_language_specific: str | None = None
    member_language: str | None = None
    cite_language: str | None = None
    problem_basic_question: str | None = None
    problem_follow_up_question: str | None = None
    possible_answers: list[str] | None = None


def pick_a_an(text):
    if text[0] in {'a', 'e', 'i', 'o', 'u'}:
        return 'an'
    return 'a'


def to_capital(text):
    return text.capitalize()


def get_names():
    gender = random.choice(['female', 'male'])
    if gender == 'female':
        name1 = random.choice(names['female_names'])
        name2 = random.choice(names['male_names'])
    else:
        name1 = random.choice(names['male_names'])
        name2 = random.choice(names['female_names'])

    return name1, name2


def create_entity_basic_details():
    entity = BusinessEntity()
    entity.foreign = random.choice([True, False])
    entity.per_se = random.choice([True, False])

    if entity.per_se:
        entity = pick_per_se_corporation(entity)
    elif entity.foreign:
        entity = pick_foreign_eligible_entity(entity)
    else:
        entity = pick_us_eligible_entity(entity)

    # set the liability language
    if entity.all_mems_ltd_liab:
        entity.liability_language_specific = f'All members of {entity.name} have limited liability'
        entity.liability_language_general = 'all members of the entity have limited liability'
    else:
        entity.liability_language_specific = f'At least one member of {entity.name} has unlimited liability'
        entity.liability_language_general = 'at least one member of the entity has unlimited liability'

    # set the member language
    if entity.single_member:
        entity.member_language = 'has only one member'
    else:
        entity.member_language = 'has more than one member'

    # set the elect status as the opposite of the default status
    entity.elect = not entity.default

    return entity


def pick_per_se_corporation(entity: BusinessEntity):
    if entity.foreign:
        # some countries do not have per se corps (e.g., BVI)
        # iterate through countries until you find one that does
        while True:
            selected_country = random.choice(country_data)
            if selected_country['per se corporation']:
                break
        entity.country_or_state = selected_country['country_name']
        entity.type_long_form = selected_country['per se corporation']
        entity.type_short_form = selected_country['per se corporation abbreviation']
        entity.language = selected_country['language']

    # a US entity
    else:
        entity.country_or_state = random.choice(states)
        entity.type_long_form = US_data['per se corporation']
        entity.type_short_form = random.choice(US_data['per se corporation abbreviations'])
        entity.language = US_data['language']  # 'English'

    entity.all_mems_ltd_liab = True  # all per se corps have ltd liab
    entity.single_member = random.choice([True, False])  # doesn't really matter here
    entity.default = random.choice([True, False])  # doesn't really matter here
    entity.name = random.choice(animals_by_country[entity.language])

    return entity


def pick_foreign_eligible_entity(entity: BusinessEntity):
    entity.all_mems_ltd_liab = random.choice([True, False])
    entity.single_member = random.choice([True, False])
    entity.default = random.choice([True, False])

    if entity.all_mems_ltd_liab:  # e.g., foreign LLC or LLP
        while True:
            selected_country = random.choice(country_data)

            # usually only one of these, but some have two
            # Chile (SRL & SpA), France (SAS & SARL), and Singapore (Pte. Ltd & LLP)
            type_of_entity = random.choice(selected_country['eligible with limited liability'])

            # some countries do not have elig. entities with ltd. liab (e.g., Canada and NZ)
            # if there is a name for the elig. entity with ltd. liab, then one exists and pick that cn
            if type_of_entity['name']:
                break
        entity.country_or_state = selected_country['country_name']
        entity.type_long_form = type_of_entity['name']
        entity.type_short_form = type_of_entity['abbreviation']
        entity.language = selected_country['language']

        entity.name = random.choice(animals_by_country[entity.language])

        # LLPs cannot have a single member
        if entity.type_short_form in ['LLP']:
            entity.single_member = False

    else:  # not all members have limited liability (e.g., foreign GP, LP, ULC, or SCI)
        # some countries do not have these; iterate through countries until you find one that does
        while True:
            selected_country = random.choice(country_data)

            # Canada (ULC), Colombia (SC), and France (SCI) have one
            # Cayman Islands (GP, LP), Singapore (GP, LP) and the UK (GP, LP) have two
            type_of_entity = random.choice(selected_country['eligible with unlimited liability'])

            # if there is a name for the elig entity with unltd liab, then one exists and pick that cn
            if type_of_entity['name']:
                break
        entity.country_or_state = selected_country['country_name']
        entity.type_long_form = type_of_entity['name']
        entity.type_short_form = type_of_entity['abbreviation']
        entity.language = selected_country['language']
        entity.name = random.choice(animals_by_country[entity.language])

        # # only ULCs, SCs, and SCIs can generally be single member entities with unltd liab
        # if not a ULC, SC, or SCI, make multi-member
        if entity.type_short_form not in ['ULC', 'SC', 'SCI']:
            entity.single_member = False

    return entity


def pick_us_eligible_entity(entity: BusinessEntity):
    entity.default = random.choice([True, False])
    entity.single_member = random.choice([True, False])

    # whether all members have ltd liab matters here only to determ the type of entity chosen
    entity.all_mems_ltd_liab = random.choice([True, False])

    if entity.all_mems_ltd_liab:
        type_of_entity = random.choice(US_data['eligible with limited liability'])  # LLC or LLP
    else:
        type_of_entity = random.choice(US_data['eligible with unlimited liability'])  # GP or LP

    entity.type_long_form = type_of_entity['name']
    entity.type_short_form = type_of_entity['abbreviation']
    entity.country_or_state = random.choice(states)
    entity.language = US_data['language']  # 'English'
    entity.name = random.choice(animals_by_country[entity.language])

    # LLPs, GPs, and LPs generally cannot have a single member
    if entity.type_short_form in ['LLP', 'GP', 'LP']:
        entity.single_member = False

    return entity


def create_basic_question(entity: BusinessEntity):
    entity.problem_basic_question = f'{entity.name}, {entity.type_short_form} is organized in {entity.country_or_state} as {pick_a_an(entity.type_long_form.lower())} {entity.type_long_form}. {entity.name}, {entity.type_short_form} {entity.member_language}. {entity.liability_language_specific}. Is {entity.name}, {entity.type_short_form} eligible to check the box?'
    return entity


def create_follow_up_question(entity: BusinessEntity):
    if entity.default:
        entity.problem_follow_up_question = 'If so, what is its default status if there is no election under the check-the-box rules?'
    else:
        entity.problem_follow_up_question = 'If so, what type of entity will it be if there is an election under the check-the-box rules (that is, if the entity does not take default status under the check-the-box rules)?'
    return entity


def set_possible_answers(entity: BusinessEntity, no_because_per_se):
    if entity.default:
        entity.possible_answers = [no_because_per_se, yes_default_dre, yes_default_pship, yes_default_corp]
    else:  # an election was made
        entity.possible_answers = [no_because_per_se, yes_elect_dre, yes_elect_pship, yes_elect_corp]
    return entity


def create_responses_per_se(entity: BusinessEntity, correct_per_se):
    responses = {}
    responses[entity.possible_answers[0]] = correct_per_se
    responses[entity.possible_answers[1]] = wrong_per_se
    responses[entity.possible_answers[2]] = wrong_per_se
    responses[entity.possible_answers[3]] = wrong_per_se
    return responses


def create_responses_elig_fgn_default(entity: BusinessEntity, correct_elig_fgn_default):
    responses = {}
    responses[entity.possible_answers[0]] = wrong_per_se
    if entity.all_mems_ltd_liab:
        responses[entity.possible_answers[1]] = wrong_elig_fgn_default
        responses[entity.possible_answers[2]] = wrong_elig_fgn_default
        responses[entity.possible_answers[3]] = correct_elig_fgn_default
    else:  # unlimited liability
        if entity.single_member:
            responses[entity.possible_answers[1]] = correct_elig_fgn_default
            responses[entity.possible_answers[2]] = wrong_elig_fgn_default
        else:  # multi-member
            responses[entity.possible_answers[1]] = wrong_elig_fgn_default
            responses[entity.possible_answers[2]] = correct_elig_fgn_default
        responses[entity.possible_answers[3]] = wrong_elig_fgn_default
    return responses


def create_responses_elig_fgn_elect(entity: BusinessEntity, correct_elig_fgn_elect):
    responses = {}
    responses[entity.possible_answers[0]] = wrong_per_se
    if entity.all_mems_ltd_liab:
        if entity.single_member:
            responses[entity.possible_answers[1]] = correct_elig_fgn_elect
            responses[entity.possible_answers[2]] = wrong_elig_fgn_elect
        else:  # multi-member
            responses[entity.possible_answers[1]] = wrong_elig_fgn_elect
            responses[entity.possible_answers[2]] = correct_elig_fgn_elect
        responses[entity.possible_answers[3]] = wrong_elig_fgn_elect
    else:  # unlimited liability
        responses[entity.possible_answers[1]] = wrong_elig_fgn_elect
        responses[entity.possible_answers[2]] = wrong_elig_fgn_elect
        responses[entity.possible_answers[3]] = correct_elig_fgn_elect
    return responses


def create_responses_elig_us_default(entity: BusinessEntity, correct_elig_us_default):
    responses = {}
    responses[entity.possible_answers[0]] = wrong_per_se
    if entity.single_member:
        responses[entity.possible_answers[1]] = correct_elig_us_default
        responses[entity.possible_answers[2]] = wrong_elig_us_default
    else:  # multi-member
        responses[entity.possible_answers[1]] = wrong_elig_us_default
        responses[entity.possible_answers[2]] = correct_elig_us_default
    responses[entity.possible_answers[3]] = wrong_elig_us_default
    return responses


def create_responses_elig_us_elect(entity: BusinessEntity, correct_elig_us_elect):
    responses = {}
    responses[entity.possible_answers[0]] = wrong_per_se
    responses[entity.possible_answers[1]] = wrong_elig_us_elect
    responses[entity.possible_answers[2]] = wrong_elig_us_elect
    responses[entity.possible_answers[3]] = correct_elig_us_elect
    return responses


def create_entity_and_responses():
    entity = create_entity_basic_details()
    entity = create_basic_question(entity)
    entity = create_follow_up_question(entity)

    # set the variable potential answer
    no_because_per_se = f'No, because {pick_a_an(entity.type_long_form.lower())} {entity.type_long_form} organized in {entity.country_or_state} is a per se corporation.'

    # create the possible answers
    entity = set_possible_answers(entity, no_because_per_se)

    # variable response components
    genl_stmt_no_per_se = f'{pick_a_an(entity.type_long_form.lower()).capitalize()} {entity.type_long_form} is not a per se corporation under this regulation and is therefore eligible to check the box.'

    correct_per_se = f'<p {style_green}>That is correct. {genl_explanation} {to_capital(pick_a_an(entity.type_long_form.lower()))} {entity.type_long_form} organized in {entity.country_or_state} is a per se corporation under {cite_per_se_foreign if entity.foreign else cite_per_se_us}.</p>'

    elig_fgn_default_status = 'corporation' if entity.all_mems_ltd_liab else 'disregarded entity' if entity.single_member else 'partnership'
    elig_fgn_elect_status = (
        'corporation' if not entity.all_mems_ltd_liab else 'disregarded entity' if entity.single_member else 'partnership'
    )
    elig_us_default_status = 'disregarded entity' if entity.single_member else 'partnership'
    elig_us_elect_status = 'corporation'

    correct_elig_fgn_default = f'<p {style_green}>That is correct. {genl_explanation} {genl_stmt_no_per_se} {cite_elig_fgn_default} states that a foreign entity in which {entity.liability_language_general} and that {entity.member_language} defaults to {pick_a_an(elig_fgn_default_status)} {elig_fgn_default_status}.</p>'

    correct_elig_fgn_elect = f'<p {style_green}>That is correct. {genl_explanation} {genl_stmt_no_per_se} {cite_elig_fgn_elect_correct} states that a foreign entity in which {entity.liability_language_general} and that {entity.member_language} may elect to be {pick_a_an(elig_fgn_elect_status)} {elig_fgn_elect_status}.</p>'

    correct_elig_us_default = f'<p {style_green}>That is correct. {genl_explanation} {genl_stmt_no_per_se} {cite_elig_us_default_or_elect} states a domestic (U.S.) entity which {entity.member_language} defaults to {pick_a_an(elig_us_default_status)} {elig_us_default_status}.</p>'

    correct_elig_us_elect = f'<p {style_green}>That is correct. {genl_explanation} {genl_stmt_no_per_se} {cite_elig_us_default_or_elect} states a domestic (U.S.) entity which is not a per se corporation may, regardless of its number of members, elect into {pick_a_an(elig_us_elect_status)} {elig_us_elect_status}.</p>'

    # create the responses
    if entity.per_se:
        responses = create_responses_per_se(entity, correct_per_se)
    elif entity.foreign and entity.default:
        responses = create_responses_elig_fgn_default(entity, correct_elig_fgn_default)
    elif entity.foreign and entity.elect:
        responses = create_responses_elig_fgn_elect(entity, correct_elig_fgn_elect)
    elif not entity.foreign and entity.default:
        responses = create_responses_elig_us_default(entity, correct_elig_us_default)
    elif not entity.foreign and entity.elect:
        responses = create_responses_elig_us_elect(entity, correct_elig_us_elect)

    return entity, responses


@app.route('/resources/practice/check_the_box')
def index():
    member_name1, member_name2 = get_names()
    entity, responses = create_entity_and_responses()
    return render_template(
        'index_new.html',
        problem=entity.problem_basic_question + ' ' + entity.problem_follow_up_question,
        responses=responses,
        entity=entity,
        member_name1=member_name1,
        member_name2=member_name2,
        canonical='https://www.andrewmitchel.com/resources/practice/check_the_box',
    )


# static & global misc strings
treas = 'Treas. Reg. §'
corn_reg = 'https://www.law.cornell.edu/cfr/text/26/'
style_green = 'style="background-color: rgba(193, 254, 93, 0.5);"'
style_red = 'style="background-color: rgba(254, 113, 93, 0.5);"'

# static & global citations
cite_per_se_foreign = f'<a href="{corn_reg}301.7701-2#b">{treas}301.7701-2(b)(8)</a>'
cite_per_se_us = f'<a href="{corn_reg}301.7701-2#b">{treas}301.7701-2(b)(1)</a>'
cite_per_se_general = f'<a href="{corn_reg}301.7701-2#b">{treas}301.7701-2(b)</a>'
cite_elig_fgn_default = f'<a href="{corn_reg}301.7701-3#b">{treas}301.7701-3(b)(2)(i)</a>'
cite_elig_fgn_elect_correct = f'<a href="{corn_reg}301.7701-3#b">{treas}301.7701-3(b)(2)(i)</a>'
cite_elig_fgn_elect_wrong = f'<a href="{corn_reg}301.7701-3">{treas}301.7701-3(a) and (b)</a>'
cite_elig_us_default_or_elect = f'<a href="{corn_reg}301.7701-3#b">{treas}301.7701-3(b)(1)</a>'
cite_elig_general = f'<a href="{corn_reg}301.7701-3">{treas}301.7701-3(a)</a>'

# static & global potential answers
yes_default_dre = 'Yes, and its default status is a disregarded entity.'
yes_default_pship = 'Yes, and its default status is a partnership.'
yes_default_corp = 'Yes, and its default status is a corporation.'
yes_elect_dre = 'Yes, and its elective status is a disregarded entity.'
yes_elect_pship = 'Yes, and its elective status is a partnership.'
yes_elect_corp = 'Yes, and its elective status is a corporation.'

# static & global response components
genl_explanation = f'Under {cite_elig_general}, an entity is eligible to elect its business classification if and only if it is not classified as a corporation under {cite_per_se_general} -- that is, if and only if it is not a per se corporation.'

wrong_per_se = f'<p {style_red}>Consider what constitutes a per se corporation, as described in {cite_per_se_general}.</p>'

wrong_elig_fgn_default = f'<p {style_red}>Consider the default status discussed in {cite_elig_fgn_default}. Focus on how many members the entity has and whether any member has unlimited liability.</p>'

wrong_elig_fgn_elect = f'<p {style_red}>Consider the elective status discussed in {cite_elig_fgn_elect_wrong}. Focus on how many members the entity has and whether any member has unlimited liability.</p>'

wrong_elig_us_default = f'<p {style_red}>Consider the default status discussed in {cite_elig_us_default_or_elect}. Focus on how many members the entity has.</p>'

wrong_elig_us_elect = (
    f'<p {style_red}>Consider the elective status discussed in {cite_elig_us_default_or_elect} for domestic (U.S.) entities.</p>'
)

if __name__ == '__main__':
    app.run(debug=False)
application = app
