#!/usr/bin/env python3
"""
Renders a page from jinja2 template into html file
"""
import typing
import jinja2
from pathlib import Path
import shutil
import json
import subprocess
import time

SOURCE_PATH = Path("src").absolute()
BUILD_OUTPUT_PATH = Path("build").absolute()
BUILD_ROOT_PATH = BUILD_OUTPUT_PATH / "root"
DIST_PATH = BUILD_OUTPUT_PATH / "dist"

def render_template(
		environment: jinja2.Environment,
		template_name: str,
		context: dict[str, typing.Any] | None = None,
		output_path: Path | None = None
	) -> None:
	template = environment.get_template(template_name)
	context = context or {}
	context["open_relative"] = lambda path: ((SOURCE_PATH / template_name).parent / path).open()
	content = template.render(**context or {})
	if output_path is None:
		output_path = (BUILD_ROOT_PATH / template_name)
	else:
		output_path = BUILD_ROOT_PATH / output_path
	output_path.parent.mkdir(parents=True, exist_ok=True)
	with output_path.open("w+") as f:
		f.write(content)
	print(f"Rendering template {repr(template_name)}")

class ProjectMetadata(typing.TypedDict):
	display_name: str
	tags: list[str]
class PostMetadata(typing.TypedDict):
	id: str
	title: str
	published_at: str
	updated_at: typing.NotRequired[str]
	

def main() -> None:
	try:
		shutil.rmtree(BUILD_OUTPUT_PATH)
	except FileNotFoundError:
		pass
	environment = jinja2.Environment(
		loader=jinja2.FileSystemLoader([str(SOURCE_PATH)])
	)
	entrypoints: list[str] = []
	
	# Copy over static files
	for file_path in SOURCE_PATH.glob("**"):
		if not file_path.is_file():
			continue
		if file_path.suffix == ".html":
			continue
		relative_file_path = file_path.relative_to(SOURCE_PATH)
		destination_path = BUILD_ROOT_PATH / relative_file_path
		destination_path.parent.mkdir(parents=True, exist_ok=True)
		shutil.copyfile(file_path, destination_path)
		print(f"Copied static file {repr(str(relative_file_path))}")

	per_post_metadata: dict[str, PostMetadata] = {}
	for template_path in SOURCE_PATH.glob("posts/*/index.html"):
		post_metadata_file_path = template_path.parent / "metadata.json"
		post_slug = template_path.parent.name
		with post_metadata_file_path.open("rb") as f:
			post_metadata = json.load(f)
			per_post_metadata[post_slug] = post_metadata

		template_name = str(template_path.relative_to(SOURCE_PATH)).replace("\\", "/")
		render_template(
			environment,
			template_name,
			{
				"post_metadata": post_metadata,
			}
		)
		entrypoints.append(template_name)

	
	render_template(environment, "index.html")
	entrypoints.append("index.html")

	with (SOURCE_PATH / "projects" / "metadata.json").open() as f:
		projects_metadata = json.load(f)

	per_project_metadata: dict[str, ProjectMetadata] = {}
	for template_path in SOURCE_PATH.glob("projects/*/index.html"):
		project_slug = template_path.parent.name
		project_metadata_file_path = template_path.parent / "metadata.json"
		print(f"Parsing project metadata for {repr(project_slug)}")
		with project_metadata_file_path.open("r") as f:
			project_metadata = json.load(f)
			per_project_metadata[project_slug] = project_metadata
		template_name = str(template_path.relative_to(SOURCE_PATH)).replace("\\", "/")
		render_template(
			environment,
			template_name,
			{
				"project_metadata": project_metadata,
				"projects_metadata": projects_metadata,
				"per_post_metadata": per_post_metadata
			}
		)
		entrypoints.append(template_name)
	render_template(environment, "projects/index.html", {"per_project_metadata": per_project_metadata, "projects_metadata": projects_metadata})
	entrypoints.append("projects/index.html")

	render_template(environment, "posts/index.html", {"per_post_metadata": per_post_metadata})
	entrypoints.append("posts/index.html")

	render_template(environment, "atom.xml", {"per_post_metadata": per_post_metadata}, output_path=Path("public/atom.xml"))

	# Build with rollup
	with (BUILD_ROOT_PATH / "vite.config.js").open("w+") as f:
		inputs = {entrypoint:entrypoint for entrypoint in entrypoints}
		vite_config = {
			"mode": "mpa",
			"build": {
				"rollupOptions": {
					"input": inputs
				},
				"outDir": "../dist",
				"emptyOutDir": True,
				"sourcemap": True
			}
		}
		f.write(f"export default {json.dumps(vite_config)}")

	process = subprocess.Popen(
		[
			"npm",
			"run",
			"--",
			"vite",
			"build",
		],
		cwd=str(BUILD_ROOT_PATH),
	)
	status_code = process.wait()
	if status_code != 0:
		raise RuntimeError("vite failed to bundle")
	



main()
