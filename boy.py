from pathlib import Path

from pico2d import load_image, get_time, SDL_KEYDOWN, SDLK_SPACE
from transitions import Machine


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        image_path = Path(__file__).resolve().parent / 'animation_sheet.png'
        self.image = load_image(str(image_path))
        self.machine = Machine(
            model=self,
            states=['IDLE', 'SLEEP'],
            transitions=[
                {'trigger': 'time_out', 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'space_down', 'source': 'SLEEP', 'dest': 'IDLE'},
            ],
            initial='IDLE',
            auto_transitions=False,
        )
        self.on_enter_IDLE()  # 초기 상태는 on_enter가 호출되지 않으므로 직접 타이머 시작

    def on_enter_IDLE(self):
        self.idle_start_time = get_time()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE and self.state == 'SLEEP':
            self.space_down()

    def update(self):
        self.frame = (self.frame + 1) % 8
        if self.state == 'IDLE' and get_time() - self.idle_start_time >= 5:
            self.time_out()

    def draw(self):
        source_y = 300 if self.face_dir == 1 else 200
        if self.state == 'IDLE':
            self.image.clip_draw(self.frame * 100, source_y, 100, 100, self.x, self.y)
        elif self.state == 'SLEEP':
            # 누워서 자는 모습: 90도 회전해서 그림
            if self.face_dir == 1:
                self.image.clip_composite_draw(self.frame * 100, source_y, 100, 100,
                                               3.141592 / 2, '', self.x - 25, self.y - 25, 100, 100)
            else:
                self.image.clip_composite_draw(self.frame * 100, source_y, 100, 100,
                                               -3.141592 / 2, '', self.x + 25, self.y - 25, 100, 100)
