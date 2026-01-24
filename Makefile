.PHOHY: dev

.DEFAULT_GOAL := dev

dev:
	PYTHONPATH=. uv run manim -ql example/math_video.py
