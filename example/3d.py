from manim import *
import trimesh


class GLBScene(ThreeDScene):
    def construct(self):
        # Load GLB
        mesh = trimesh.load("./p.glb")

        # Some GLBs contain scenes
        if isinstance(mesh, trimesh.Scene):
            mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))

        vertices = mesh.vertices  # type: ignore
        faces = mesh.faces # type: ignore

        group = VGroup()

        # Limit polygons for performance
        for face in faces[:1500]:
            pts = [vertices[i] for i in face]

            poly = Polygon(
                *pts,
                stroke_width=0.2,
                fill_opacity=0.8,
            )

            group.add(poly)

        group.scale(2)

        self.set_camera_orientation(
            phi=70 * DEGREES,
            theta=45 * DEGREES,
        )

        self.play(Create(group), run_time=3)

        self.begin_ambient_camera_rotation(rate=0.2)

        self.wait(5)
