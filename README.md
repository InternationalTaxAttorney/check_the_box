# Check the Box Practice Problems

Randomly generated practice problems on the U.S. check-the-box entity classification rules ([Treas. Reg. § 301.7701-2](https://www.law.cornell.edu/cfr/text/26/301.7701-2) and [§ 301.7701-3](https://www.law.cornell.edu/cfr/text/26/301.7701-3)).

Each problem describes a U.S. or foreign business entity (its type, where it is organized, its number of members, and whether its members have limited liability) and asks whether the entity is eligible to check the box and, if so, what its default or elective classification is. A diagram of the members and the entity is drawn with [Mermaid](https://mermaid.js.org/), and each answer comes with an explanation and citations to the regulations.

See it live at [Practice Problems on Check-the-Box Rules](https://www.andrewmitchel.com/resources/check_the_box).

## Credit

This project extends Professor [Sarah Lawsky's](https://www.sarahlawsky.org/) [Practice Problems](https://www.lawskypracticeproblems.org/) for check-the-box elections by adding a chart of the members and the entity. Because it is based on her AGPL-licensed code, this project is also licensed under the [GNU Affero General Public License v3](LICENSE).

## Project layout

```
check_the_box/
├── pyproject.toml
├── src/check_the_box/
│   ├── __init__.py              exports ctb_bp (the Flask Blueprint)
│   ├── ctb.py                   problem generation, answers, explanations, and the route
│   ├── app.py                   minimal standalone Flask app
│   ├── data/                    JSON data (countries and entity types, states, entity and member names)
│   └── templates/
│       ├── header_footer.html   bare Bootstrap page, used only when the host app doesn't provide its own
│       └── check_the_box/check_the_box.html
└── tests/test_ctb.py
```

## Running it locally

Requires [uv](https://docs.astral.sh/uv/) and Python 3.13+.

```
git clone https://github.com/InternationalTaxAttorney/check_the_box.git
cd check_the_box
uv sync
uv run check-the-box
```

Then open http://127.0.0.1:5000/ (it redirects to `/resources/check_the_box`).

## Using it in another Flask app

The problems are served by a Flask Blueprint named `ctb` with one route, `/resources/check_the_box` (endpoint `ctb.check_the_box`).

Add the package as a dependency, pinned to a release tag:

```
uv add "check-the-box @ git+https://github.com/InternationalTaxAttorney/check_the_box@v1.0.0"
```

Then register the Blueprint:

```python
from check_the_box import ctb_bp

app.register_blueprint(ctb_bp)
```

The page template starts with `{% extends 'header_footer.html' %}` and fills `{% block content %}`. Flask searches the host app's `templates` folder before the Blueprint's, so if your app has its own `header_footer.html`, the problems page uses your site's header and footer. To change the page itself, put your own copy at `templates/check_the_box/check_the_box.html` in your app.

Your `header_footer.html` should load Bootstrap 5, because the page uses Bootstrap classes. The page receives a `canonical` variable that your header can use for a `<link rel="canonical">` tag.

## Development

```
uv run pytest
uv run ruff check .
```

The tests generate a few thousand random problems and check that each one has four answer choices with exactly one correct answer.

### Editing the data

- `data/country_data.json`: for each country, the per se corporation and the eligible entity types with limited and unlimited liability. Use an empty string for a type the country does not have (e.g., the Cayman Islands has no per se corporation).
- `data/us_data.json`: the same for U.S. entities.
- `data/animalsbycountry.json`: entity names by language. Each `language` in the country data must appear here.
- `data/names.json`: female and male names for members.
- `data/states.json`: the 50 states.

### Releasing a new version

1. Update `version` in `pyproject.toml` and add an entry to `CHANGELOG.md`.
2. Run the tests.
3. Commit, tag, and push: `git tag v1.0.1` and then `git push --follow-tags`.
4. In any site that uses the package, update the tag in its `pyproject.toml` and run `uv lock`.

## License

[GNU Affero General Public License v3.0 or later](LICENSE). If you run a modified version of this code on a public website, the AGPL requires you to make your modified source code available to the site's users.
