.PHOHY: dev

.DEFAULT_GOAL := dev

dev:
	PYTHONPATH=. uv run manim -pql example/3d.py

build: clean
	PYTHONPATH=. uv run manim -pqh example/car_pulley.py

clean:
	rm -rf ./media/*
