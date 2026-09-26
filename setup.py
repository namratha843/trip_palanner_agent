from pathlib import Path
from setuptools import find_packages, setup

BASE_DIR = Path(__file__).parent

README = (BASE_DIR / "README.md").read_text(encoding="utf-8")

requirements = []
requirements_file = BASE_DIR / "requirements.txt"
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="trip-planner",
    version="0.1.0",
    description="Trip planner agent",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.10",
)