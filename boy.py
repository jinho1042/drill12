from pathlib import Path

from pico2d import (load_image, get_time, get_canvas_width, clamp,
                    SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT, SDLK_a)
from transitions import Machine


class AutoRun:
    """자동 무적 런: 키 조작 없이 빠르게 좌우를 오가고, 크기가 커진다."""
    SPEED = 15
    SCALE = 2
    DURATION = 5

    @staticmethod
    def enter(boy):
        boy.dir = boy.face_dir
        boy.invincible = True
        boy.auto_run_start_time = get_time()

    @staticmethod
    def exit(boy):
        boy.invincible = False

    @staticmethod
    def do(boy):
        if get_time() - boy.auto_run_start_time >= AutoRun.DURATION:
            boy.auto_run_time_out()
            return
        half_width = 25 * AutoRun.SCALE
        boy.x += boy.dir * AutoRun.SPEED
        # 화면 끝에 닿으면 방향 전환
        if boy.x <= half_width or boy.x >= get_canvas_width() - half_width:
            boy.dir = boy.face_dir = -boy.dir
        boy.x = clamp(half_width, boy.x, get_canvas_width() - half_width)

    @staticmethod
    def draw(boy):
        source_y = 100 if boy.dir == 1 else 0
        size = 100 * AutoRun.SCALE
        # 발 위치가 그대로 땅에 닿도록 커진 만큼 위로 올려서 그림
        boy.image.clip_draw(boy.frame * 100, source_y, 100, 100,
                            boy.x, boy.y + (size - 100) // 2, size, size)


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0  # 달리는 방향: -1 왼쪽, 1 오른쪽
        self.invincible = False
        image_path = Path(__file__).resolve().parent / 'animation_sheet.png'
        self.image = load_image(str(image_path))
        self.machine = Machine(
            model=self,
            states=['IDLE', 'SLEEP', 'RUN', 'AUTO_RUN'],
            transitions=[
                {'trigger': 'time_out', 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'space_down', 'source': 'SLEEP', 'dest': 'IDLE'},
                {'trigger': 'arrow_down', 'source': ['IDLE', 'SLEEP', 'AUTO_RUN'], 'dest': 'RUN'},
                {'trigger': 'arrow_up', 'source': 'RUN', 'dest': 'IDLE'},
                {'trigger': 'a_down', 'source': 'IDLE', 'dest': 'AUTO_RUN'},
                {'trigger': 'auto_run_time_out', 'source': 'AUTO_RUN', 'dest': 'IDLE'},
            ],
            initial='IDLE',
            auto_transitions=False,
        )
        self.on_enter_IDLE()  # 초기 상태는 on_enter가 호출되지 않으므로 직접 타이머 시작

    def on_enter_IDLE(self):
        self.dir = 0
        self.idle_start_time = get_time()

    def on_enter_AUTO_RUN(self):
        AutoRun.enter(self)

    def on_exit_AUTO_RUN(self):
        AutoRun.exit(self)

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE and self.state == 'SLEEP':
            self.space_down()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_a and self.state == 'IDLE':
            self.a_down()
        elif event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
            # 방향만 바꾸면 되므로 RUN 중에 반대 방향키를 눌러도 같은 RUN 상태에서 처리
            self.dir = self.face_dir = -1 if event.key == SDLK_LEFT else 1
            if self.state in ('IDLE', 'SLEEP', 'AUTO_RUN'):
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
        elif self.state == 'AUTO_RUN':
            AutoRun.do(self)

    def draw(self):
        source_y = 300 if self.face_dir == 1 else 200
        if self.state == 'IDLE':
            self.image.clip_draw(self.frame * 100, source_y, 100, 100, self.x, self.y)
        elif self.state == 'RUN':
            source_y = 100 if self.dir == 1 else 0
            self.image.clip_draw(self.frame * 100, source_y, 100, 100, self.x, self.y)
        elif self.state == 'AUTO_RUN':
            AutoRun.draw(self)
        elif self.state == 'SLEEP':
            # 누워서 자는 모습: 90도 회전해서 그림
            if self.face_dir == 1:
                self.image.clip_composite_draw(self.frame * 100, source_y, 100, 100,
                                               3.141592 / 2, '', self.x - 25, self.y - 25, 100, 100)
            else:
                self.image.clip_composite_draw(self.frame * 100, source_y, 100, 100,
                                               -3.141592 / 2, '', self.x + 25, self.y - 25, 100, 100)
