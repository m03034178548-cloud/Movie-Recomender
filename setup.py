from setuptools import setup, find_packages

AUTHOR_NAME = "RAZA_CHEETA, AHMAD_KHAN"
LIST_OF_REQUIREMENTS = ["streamlit"]

setup(
    name="movie_recommender",
    version="0.0.1",
    author=AUTHOR_NAME,
    author_email="murshadraza11@gmail.com",
    description="A small example package for movies recommendation",
    long_description="Movie recommender package",
    long_description_content_type="text/markdown",
    packages=find_packages(),  # find packages in current folder
    python_requires=">=3.7",
    install_requires=LIST_OF_REQUIREMENTS,
)
