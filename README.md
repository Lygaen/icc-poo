# Object-Oriented Programmation - Game

EPFL's 2025 autumn programmation project. The project was a game, using the [arcade.py](https://api.arcade.academy/en/stable/) library. It was made with [Martin Gremeaux-Bader](https://people.epfl.ch/martin.gremeaux-bader).

> If viewing outside of the GitHub repository, the rendering of the svgs in `images` in the `DESIGN.md` file might break.
> Try opening the [repository on GitHub](https://github.com/Lygaen/icc-poo) if having rendering issues.

## How to play / use
First of all, you need to clone this repository :
```sh
git clone https://github.com/Lygaen/icc-poo
```

At the same time, you will need to have [UV](https://astral.sh/uv/) installed. Then you can do :
```sh
cd icc-poo
uv sync
```

To run the game, simply do :
```sh
uv run main.py
```

### Tests
The tests are ran using [PyTest](https://pytest.org/). To run a test, use :
```sh
uv run pytest
```

The tests for benchmarks are skipped by default because of the long time they take. To run them anyway, do :
```sh
uv run pytest --runslow
```

### MyPy
This project uses mypy for type-checking. To run mypy for this project, use :
```sh
uv run mypy .
```

## Course
This repository follows the 2025's autumn ICC (*CS-112(j)*) project. The course was taught by [Sébastien Doeraene](https://people.epfl.ch/sebastien.doeraene).

It was taught over [here mainly](https://epfl-cs-112-ma.github.io/).

## Usage
This projects uses, as prescribed by the course :
- [UV](https://astral.sh/uv/) as a project / version manager
- [PyTest](https://pytest.org/) for testing / coverage
- [MyPy](https://mypy-lang.org/) for a stronger typing system
