import os
import sys
import typing

import jinja2


def get_template_env() -> jinja2.Environment:
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)

    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def format_transcript_with_template(
    lines: typing.List[typing.Tuple[str, str, str]],
    template_name: str,
    speaker_map: typing.Optional[typing.Dict[str, str]] = None,
) -> str:
    if speaker_map is None:
        speaker_map = {}

    # Apply speaker mapping
    mapped_lines = []
    for timestamp, speaker, text in lines:
        mapped_speaker = speaker_map.get(speaker, speaker)
        mapped_lines.append((timestamp, mapped_speaker, text))

    env = get_template_env()

    try:
        template = env.get_template(f"{template_name}.j2")
    except jinja2.exceptions.TemplateNotFound:
        print(
            f"Template '{template_name}' not found. Using default template.",
            file=sys.stderr,
        )
        template = env.get_template("default.j2")

    return template.render(lines=mapped_lines)


def list_available_templates() -> None:
    env = get_template_env()
    templates = env.list_templates(extensions=["j2"])
    if not templates:
        print("No templates found.")
    else:
        print("Available templates:")
        for template in templates:
            print(f"  - {os.path.splitext(template)[0]}")
