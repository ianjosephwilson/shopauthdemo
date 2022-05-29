from distutils.core import setup


setup(
    name="shopauthdemo",
    version="0.1.0b",
    description="Demo of the shopauth library.",
    author="Ian Wilson",
    author_email="ian@laspilitas.com",
    url="https://www.github.com/ianjosephwilson/shopauthdemo",
    install_requires=[
        "pyramid",
        "pyramid_tm",
        "sqlalchemy",
        "zope.sqlalchemy",
        "gunicorn",
        "python-dotenv",
    ],
    packages=["shopauthdemo"],
    package_dir={"shopauthdemo": "shopauthdemo"},
    include_package_data=True,
    zip_safe=False,
    extras_require={"dev": ["black", "flake8"]},
)
