# mlb-hof-scraper

A utility Python package designed to download data from Hall of Fame voting data from [baseball-reference.com](https://www.baseball-reference.com/).
The tool is designed to download and return the data as a `pd.Dataframe` object so it can be used in other Python projects.
This is not a full-fledged supported tool that will be regularly maintained.
Just needed to create a tool with this functionality and figured that I would make it into a Python package.
Maybe one day I'll add to my fork of the [sportsipy](https://github.com/roclark/sportsipy) project to include this extra functionality.
I just didn't feel like doing it now since this doesn't really build on the structuire that is already in that repo.

## Installation
You need to have git installed on your machine to install this package.
```
pip install git+https://github.com/samkasbawala/mlb-hof-scraper.git
```

## Todo
- Add tests lol
- Add players that have been voted in by the veterens committee
- If there is no table on a valid page, then None should be returned
