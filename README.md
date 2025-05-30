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

It was taught over [here](https://epfl-cs-112-ma.github.io/) mainly.

## Usage
This projects uses, as prescribed by the course :
- [UV](https://astral.sh/uv/) as a project / version manager
- [PyTest](https://pytest.org/) for testing / coverage
- [MyPy](https://mypy-lang.org/) for a stronger typing system

## Extensions
We added two extensions to this project:
- Invisible blocs with no collisions, but count as a part of moving platform groups, so we can synchronize seemingly disjoints groups movement without flooding the yaml map with arrows everywhere.
- A health points system : every creature (player and monsters) has health points. The damage is inflicted when a monster touches the player, or if the sword or an arrow hits a monster. The damage is inflicted raw, and every creature gains invincibility for a short time after being hurt. Health points and damage stats vary between creature and weapons. In addition, when the player is hurt (by direct contact with a monster), a knockback is applied to it to avoid it to just run through monsters.