from manim import *

from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService


class AzureVoiceSync(VoiceoverScene):
    def construct(self):
        service = AzureService(
            voice="en-HK-SamNeural",
        )
        self.set_speech_service(service)

        circle = Circle()

        with self.voiceover(text="This circle appears now") as tracker:
            self.play(Create(circle), run_time=tracker.duration)

        with self.voiceover(text="Now it becomes a square"):
            self.play(Transform(circle, Square()))
