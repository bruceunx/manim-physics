.PHOHY: dev

.DEFAULT_GOAL := dev

dev:
	PYTHONPATH=. uv run manim -pql example/car_pulley.py
