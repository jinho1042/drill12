from pathlib import Path

from pico2d import (load_image, get_time, get_canvas_width, clamp,
                    SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT)
from transitions import Machine


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0  # 달리는 방향: -1 왼쪽, 1 오른쪽
        image_path = Path(__file__).resolve().parent / 'animation_sheet.png'
        self.image = load_image(str(image_path))
        self.machine = Machine(
            model=self,
            states=['IDLE', 'SLEEP', 'RUN'],
            transitions=[
                {'trigger': 'time_out', 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'space_down', 'source': 'SLEEP', 'dest': 'IDLE'},
                {'trigger': 'arrow_down', 'source': ['IDLE', 'SLEEP'], 'dest': 'RUN'},
                {'trigger': 'arrow_up', 'source': 'RUN', 'dest': 'IDLE'},
            ],
            initial='IDLE',
            auto_transitions=False,
        )
        self.on_enter_IDLE()  # 초기 상태는 on_enter가 호출되지 않으므로 직접 타이머 시작

    def on_enter_IDLE(self):
        self.dir = 0
        self.idle_start_time = get_time()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE and self.state == 'SLEEP':
            self.space_down()
        elif event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
            # 방향만 바꾸면 되므로 RUN 중에 반대 방향키를 눌러도 같은 RUN 상태에서 처리
            self.dir = self.face_dir = -1 if event.key == SDLK_LEFT else 1
            if self.state in ('IDLE', 'SLEEP'):
                self.arrow_down()
        elif event.type == SDL_KEYUP and event.key in (SDLK_LEFT, SDLK_RIGHT) and self.state == 'RUN':
            self.arrow_up()

    def update(self):
        self.frame = (self.frame + 1) % 8
        if self.state == 'IDLE' and get_time() - self.idle_start_time >= 5:
            self.time_out()
        elif self.state == 'RUN':
            self.x += self.dir * 5
            self.x = clamp(25, self.x, get_canvas_width() - 25)  # 화면 밖으로 나가지 않게

    def draw(self):
        source_y = 300 if self.face_dir == 1 else 200
        if self.state == 'IDLE':
            self.image.clip_draw(self.frame * 100, source_y, 100, 100, self.x, self.y)
        elif self.state == 'RUN':
            source_y = 100 if self.dir == 1 else 0
            self.image.clip_draw(self.frame * 100, source_y, 100, 100, self.x, self.y)
        elif self.state == 'SLEEP':
            # 누워서 자는 모습: 90도 회전해서 그림
            if self.face_dir == 1:
                self.image.clip_composite_draw(self.frame * 100, source_y, 100, 100,
                                               3.141592 / 2, '', self.x - 25, self.y - 25, 100, 100)
            else:
                self.image.clip_composite_draw(self.frame * 100, source_y, 100, 100,
                                               -3.141592 / 2, '', self.x + 25, self.y - 25, 100, 100)
