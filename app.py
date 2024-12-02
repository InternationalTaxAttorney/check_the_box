import json
import os
import random

from dotenv import load_dotenv
from flask import Flask, redirect, render_template

with open("json/animalsbycountry.json", "r", encoding="utf-8") as f:
    animals_by_country = json.load(f)

with open("json/country_data.json", "r", encoding="utf-8") as f:
    country_data = json.load(f)

with open("json/names.json", "r", encoding="utf-8") as f:
    names = json.load(f)

with open("json/states.json", "r", encoding="utf-8") as f:
    states = json.load(f)

with open("json/us_data.json", "r", encoding="utf-8") as f:
    US_data = json.load(f)


class BusinessEntity:
    def __init__(self, country, entity_type, entity_suffix, entity_name, default_choice, elective_choice):
        self.country = country
        self.entity_type = entity_type
        self.entity_suffix = entity_suffix
        self.entity_name = entity_name
        self.default_choice = default_choice
        self.elective_choice = elective_choice


def pick_a_an(entity):
    if entity[0] in ["a", "e", "i", "o", "u", "A", "E", "I", "O", "U", "8"]:
        return "an"
    else:
        return "a"


def to_capital(input):
    return input.capitalize()


def get_names():
    gender = random.choice(["female", "male"])
    if gender == "female":
        name1 = random.choice(names["female_names"])
        name2 = random.choice(names["male_names"])
    else:
        name1 = random.choice(names["male_names"])
        name2 = random.choice(names["female_names"])

    return name1, name2


def create_problem_and_answers() -> tuple[str, dict, BusinessEntity, bool, bool]:
    per_se_choice = random.choice(["per se", "eligible"])

    if per_se_choice == "per se":
        foreign = random.choice([True, False])
        single_member = random.choice([True, False])
        all_members_ltd_liab = True
        entity = pick_per_se_corporation(foreign)

        liability_language = f"All members of {entity.entity_name} have limited liability."

    # an eligible entity
    else:
        while True:
            foreign = random.choice([True, False])
            single_member = random.choice([True, False])
            all_members_ltd_liab = random.choice([True, False])

            # don't select US eligible entities with one member and unlimited liabilty
            # foreign entities that default to DRE (unlimited liability with one member) are rare
            # but can be found in Canada (ULCs) and France (SCIs), and possibly elsewhere
            if not (not foreign and single_member and not all_members_ltd_liab):
                break

        entity, single_member = pick_eligible_entity(foreign, single_member, all_members_ltd_liab)

        if all_members_ltd_liab:
            liability_language = "All members of the entity have limited liability."
        else:
            liability_language = "At least one member of the entity has unlimited liability."

    if single_member:
        member_language = "has only one member."
    else:
        member_language = "has more than one member."

    problem_lang = f"{entity.entity_name}, {entity.entity_suffix} is organized in {entity.country} as {pick_a_an(entity.entity_type)} {entity.entity_type}. {entity.entity_name} {member_language} {liability_language} Is {entity.entity_name} eligible to check the box?"

    # potential answers
    no_because_per_se = f"No, because {pick_a_an(entity.entity_type)} {entity.entity_type} organized in {entity.country} is a per se corporation."
    yes_default_DRE = "Yes, and its default status is a disregarded entity."
    yes_default_partnership = "Yes, and its default status is a partnership."
    yes_default_corp = "Yes, and its default status is a corporation."
    yes_elect_DRE = "Yes, and its elective status is a disregarded entity."
    yes_elect_partnership = "Yes, and its elective status is a partnership."
    yes_elect_corp = "Yes, and its elective status is a corporation."

    general_explanation = 'Under <a href="https://www.law.cornell.edu/cfr/text/26/301.7701-3">Treas. Reg. §301.7701-3(a)</a>, an entity is eligible to elect its business classification if and only if it is not classified as a corporation under <a href="https://www.law.cornell.edu/cfr/text/26/301.7701-2#b">Treas. Reg. §301.7701-2(b)</a>--that is, if and only if it is not a per se corporation.'

    general_statement_no_per_se = f"{pick_a_an(entity.entity_type).capitalize()} {entity.entity_type} is not a per se corporation under this regulation and is therefore eligible to check the box."

    question_default_status = "If so, what is its default status if there is no election under the check-the-box rules?"

    question_if_election = "If so, what type of entity will it be if there is an election under the check-the-box rules (that is, if the entity does not take default status under the check-the-box rules)?"

    question = random.choice([question_default_status, question_if_election])
    problem = f"{problem_lang} {question}"
    judgments = {}

    if question == question_default_status:
        possible_answers = [no_because_per_se, yes_default_DRE, yes_default_partnership, yes_default_corp]

        if per_se_choice == "per se":
            correct_answer = no_because_per_se
            for possible_answer in possible_answers:
                if possible_answer == correct_answer:
                    if foreign:
                        citation = "Treas. Reg. §301.7701-2(b)(8)"
                    else:
                        citation = "Treas. Reg. §301.7701-2(b)(1)"

                    explanation = f'<p style="background-color: rgba(193, 254, 93, 0.5);">That is correct. {general_explanation} {to_capital(pick_a_an(entity.entity_type))} {entity.entity_type} organized in {entity.country} is a per se corporation under <a href="https://www.law.cornell.edu/cfr/text/26/301.7701-2#b">{citation}</a>.</p>'

                # user selected wrong answer
                else:
                    explanation = f'<p style="background-color: rgba(254, 113, 93, 0.5);">Consider what constitutes a per se corporation, as described in <a href="https://www.law.cornell.edu/cfr/text/26/301.7701-2#b">Treas. Reg. §301.7701-2(b)</a>.</p>'

                judgments[possible_answer] = explanation
        # ------------------------------------------------

        if per_se_choice == "eligible":
            correct_answer = f"Yes, and its default status is {pick_a_an(entity.default_choice)} {entity.default_choice}."
            for possible_answer in possible_answers:

                if foreign:
                    if possible_answer == correct_answer:
                        explanation = f'<p style="background-color: rgba(193, 254, 93, 0.5);">That is correct. {general_explanation} {general_statement_no_per_se} <a href="https://www.law.cornell.edu/cfr/text/26/301.7701-3#b">Treas. Reg. §301.7701-3(b)(2)(i)</a> states that a foreign entity in which {liability_language[:-1].lower()} and that {member_language[:-1].lower()} defaults to {pick_a_an(entity.default_choice)} {entity.default_choice}.</p>'
                    elif possible_answer == no_because_per_se:
                        explanation = f'<p style="background-color: rgba(254, 113, 93, 0.5);">Consider what constitutes a per se corporation, as described in <a href="https://www.law.cornell.edu/cfr/text/26/301.7701-2#b">Treas. Reg. §301.7701-2(b)</a>.</p>'
                    else:
                        explanation = f'<p style="background-color: rgba(254, 113, 93, 0.5);">Consider the default status discussed in <a href="https://www.law.cornell.edu/cfr/text/26/301.7701-3#b">Treas. Reg. §301.7701-3(b)(2)(i)</a>. Focus on how many members the entity has and whether any member has unlimited liability.</p>'

                # US entity
                else:
                    if possible_answer == correct_answer:
                        explanation = f'<p style="background-color: rgba(193, 254, 93, 0.5);">That is correct. {general_explanation} {general_statement_no_per_se} <a href="https://www.law.cornell.edu/cfr/text/26/301.7701-3#b">Treas. Reg. §301.7701-3(b)(1)</a> states a domestic (U.S.) entity which {member_language[:-1].lower()} defaults to {pick_a_an(entity.default_choice)} {entity.default_choice}.</p>'
                    elif possible_answer == no_because_per_se:
                        explanation = f'<p style="background-color: rgba(254, 113, 93, 0.5);">Consider what constitutes a per se corporation, as described in <a href="https://www.law.cornell.edu/cfr/text/26/301.7701-2#b">Treas. Reg. §301.7701-2(b)</a>.</p>'
                    else:
                        explanation = f'<p style="background-color: rgba(254, 113, 93, 0.5);">Consider the default status discussed in <a href="https://www.law.cornell.edu/cfr/text/26/301.7701-3#b">Treas. Reg. §301.7701-3(b)(1)</a>. Focus on how many members the entity has.</p>'
                judgments[possible_answer] = explanation
        # ------------------------------------------------

    if question == question_if_election:
        possible_answers = [no_because_per_se, yes_elect_DRE, yes_elect_partnership, yes_elect_corp]

        if per_se_choice == "per se":
            correct_answer = no_because_per_se
            for possible_answer in possible_answers:
                if possible_answer == correct_answer:
                    if foreign:
                        citation = "Treas. Reg. §301.7701-2(b)(8)"
                    else:
                        citation = "Treas. Reg. §301.7701-2(b)(1)"

                    explanation = f'<p style="background-color: rgba(193, 254, 93, 0.5);">That is correct. {general_explanation} {to_capital(pick_a_an(entity.entity_type))} {entity.entity_type} organized in {entity.country} is a per se corporation under <a href="https://www.law.cornell.edu/cfr/text/26/301.7701-2#b">{citation}</a>.</p>'

                else:
                    explanation = f'<p style="background-color: rgba(254, 113, 93, 0.5);">Consider what constitutes a per se corporation, as described in <a href="https://www.law.cornell.edu/cfr/text/26/301.7701-2#b">Treas. Reg. §301.7701-2(b)</a>.</p>'

                judgments[possible_answer] = explanation
        # ------------------------------------------------

        if per_se_choice == "eligible":
            correct_answer = f"Yes, and its elective status is {pick_a_an(entity.elective_choice)} {entity.elective_choice}."
            for possible_answer in possible_answers:
                if foreign:
                    if possible_answer == correct_answer:
                        if liability_language == "At least one member of the entity has unlimited liability.":
                            explanation = f'<p style="background-color: rgba(193, 254, 93, 0.5);">That is correct. {general_explanation} {general_statement_no_per_se} <a href="https://www.law.cornell.edu/cfr/text/26/301.7701-3#b_2">Treas. Reg. §301.7701-3(b)(2)(i)</a> states that a foreign entity in which {liability_language[:-1].lower()} may elect to be {pick_a_an(entity.elective_choice)} {entity.elective_choice}.</p>'
                        else:
                            explanation = f'<p style="background-color: rgba(193, 254, 93, 0.5);">That is correct. {general_explanation} {general_statement_no_per_se} <a href="https://www.law.cornell.edu/cfr/text/26/301.7701-3#b_2">Treas. Reg. §301.7701-3(b)(2)(i)</a> states that a foreign entity in which {liability_language[:-1].lower()} and that {member_language[:-1].lower()} may elect to be {pick_a_an(entity.elective_choice)} {entity.elective_choice}.</p>'
                    elif possible_answer == no_because_per_se:
                        explanation = f'<p style="background-color: rgba(254, 113, 93, 0.5);">Consider what constitutes a per se corporation, as described in <a href="https://www.law.cornell.edu/cfr/text/26/301.7701-2#b">Treas. Reg. §301.7701-2(b)</a>.</p>'
                    else:
                        explanation = f'<p style="background-color: rgba(254, 113, 93, 0.5);">Consider the elective status discussed in <a href="https://www.law.cornell.edu/cfr/text/26/301.7701-3">Treas. Reg. §301.7701-3(a) and (b)</a>. Focus on how many members the entity has and whether any member has unlimited liability.</p>'

                # US entity
                else:
                    if possible_answer == correct_answer:
                        explanation = f'<p style="background-color: rgba(193, 254, 93, 0.5);">That is correct. {general_explanation} {general_statement_no_per_se} <a href="https://www.law.cornell.edu/cfr/text/26/301.7701-3#b">Treas. Reg. §301.7701-3(b)(1)</a> states a domestic (U.S.) entity which is not a per se corporation may, regardless of its number of members, elect into {pick_a_an(entity.elective_choice)} {entity.elective_choice}.</p>'
                    elif possible_answer == no_because_per_se:
                        explanation = f'<p style="background-color: rgba(254, 113, 93, 0.5);">Consider what constitutes a per se corporation, as described in <a href="https://www.law.cornell.edu/cfr/text/26/301.7701-2#b">Treas. Reg. §301.7701-2(b)</a>.</p>'
                    else:
                        explanation = f'<p style="background-color: rgba(254, 113, 93, 0.5);">Consider the elective status discussed in <a href="https://www.law.cornell.edu/cfr/text/26/301.7701-3">Treas. Reg. §301.7701-3(a)(1)</a> for domestic (U.S.) entities.</p>'
                judgments[possible_answer] = explanation

    return problem, judgments, entity, foreign, single_member


def pick_per_se_corporation(foreign) -> BusinessEntity:
    if foreign:
        # some countries do not have these (e.g., BVI); iterate through countries until you find one that does
        while True:
            selected_country = random.choice(country_data)
            if selected_country["per se corporation"]:
                break
        country = selected_country["country_name"]
        entity_type = selected_country["per se corporation"]
        entity_suffix = selected_country["per se corporation abbreviation"]
        language = selected_country["language"]

    # a US entity
    else:
        country = random.choice(states)
        entity_type = US_data["per se corporation"]
        entity_suffix = random.choice(US_data["per se corporation abbreviations"])
        language = "English"

    entity_name = random.choice(animals_by_country[language])
    default_choice = ""
    elective_choice = ""

    return BusinessEntity(country, entity_type, entity_suffix, entity_name, default_choice, elective_choice)


def pick_eligible_entity(foreign, single_member, all_members_ltd_liab) -> tuple[BusinessEntity, bool]:
    if foreign and all_members_ltd_liab:  # e.g., foreign LLC or LLP
        # some countries do not have these (e.g., Canada and NZ); iterate through countries until you find one that does
        while True:
            selected_country = random.choice(country_data)
            country = selected_country["country_name"]
            entity_type_dict = random.choice(selected_country["eligible with limited liability"])
            if entity_type_dict["name"]:
                break
        entity_type = entity_type_dict["name"]
        entity_suffix = entity_type_dict["abbreviation"]
        entity_name = random.choice(animals_by_country[selected_country["language"]])
        default_choice = "corporation"

        # LLPs cannot have a single member
        if entity_suffix == "LLP":
            single_member = False

        if single_member:
            elective_choice = "disregarded entity"
        else:
            elective_choice = "partnership"

    elif foreign and not all_members_ltd_liab:  # e.g., foreign GP, LP, ULC, or SCI
        # some countries do not have these; iterate through countries until you find one that does
        while True:
            selected_country = random.choice(country_data)
            country = selected_country["country_name"]
            entity_type_dict = random.choice(selected_country["eligible with unlimited liability"])
            if entity_type_dict["name"]:
                break
        entity_type = entity_type_dict["name"]
        entity_suffix = entity_type_dict["abbreviation"]
        entity_name = random.choice(animals_by_country[selected_country["language"]])

        # only ULCs and SCIs can be single member entities; if not a ULC or SCI, make multi-member
        if entity_suffix not in ["ULC", "SCI"]:
            single_member = False

        if single_member:
            default_choice = "disregarded entity"
        else:
            default_choice = "partnership"
        elective_choice = "corporation"

    elif not foreign and all_members_ltd_liab:  # e.g., US LLC or LLP
        country = random.choice(states)
        entity_type_dict = random.choice(US_data["eligible with limited liability"])
        entity_type = entity_type_dict["name"]
        entity_suffix = entity_type_dict["abbreviation"]
        entity_name = random.choice(animals_by_country["English"])

        # LLPs cannot have a single member
        if entity_suffix == "LLP":
            single_member = False

        if single_member:
            default_choice = "disregarded entity"
        else:
            default_choice = "partnership"
        elective_choice = "corporation"

    elif not foreign and not all_members_ltd_liab:  # e.g., US GP or LP
        country = random.choice(states)
        entity_type_dict = random.choice(US_data["eligible with unlimited liability"])
        entity_type = entity_type_dict["name"]
        entity_suffix = entity_type_dict["abbreviation"]
        entity_name = random.choice(animals_by_country["English"])
        if single_member:
            default_choice = "disregarded entity"
        else:
            default_choice = "partnership"
        elective_choice = "corporation"

    entity = BusinessEntity(country, entity_type, entity_suffix, entity_name, default_choice, elective_choice)

    return entity, single_member


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")


app = Flask(__name__)
load_dotenv()
app.config.from_object(Config)


@app.errorhandler(404)
def page_not_found(e):
    # Redirect to another page (e.g., home page or a custom 404 page)
    return redirect("https://www.andrewmitchel.com/resources.php")


@app.route("/check_the_box")
def index():
    name1, name2 = get_names()
    problem, judgments, entity, foreign, single_member = create_problem_and_answers()
    return render_template(
        "index.html",
        problem=problem,
        judgments=judgments,
        entity=entity,
        foreign=foreign,
        single_member=single_member,
        name1=name1,
        name2=name2,
        canonical=f"https://www.andrewmitchel.com/resources/practice/check_the_box",
    )


if __name__ == "__main__":
    app.run(debug=True)
application = app

# tried to use htmx, but couldn't get mermaid to redraw the chart for Next Question
# just made Next Question refresh the page
