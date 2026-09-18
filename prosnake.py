# -*- coding: utf-8 -*-
import turtle
import time
import random
import os

# حاول تشغيل الأصوات إن توفرت (ويندوز)
try:
    import winsound
    def play_sound(fname):
        if os.path.exists(fname):
            winsound.PlaySound(fname, winsound.SND_ASYNC)
except Exception:
    def play_sound(fname):  # لا شيء (صامت)
        pass

# =============== إعدادات عامة ===============
WIDTH, HEIGHT = 800, 800
BORDER_X, BORDER_Y = WIDTH//2 - 20, HEIGHT//2 - 20

STATE_SPLASH = "splash"
STATE_MENU   = "menu"
STATE_PLAY   = "playing"
STATE_OVER   = "over"
STATE_STATS  = "stats"

delay = 0.08
score = 0
high_score = 0
level = 1
game_state = STATE_SPLASH
start_time = 0
foods_eaten = 0
last_eat_times = []          # لتتبع الـCombo
COMBO_WINDOW_S = 10

# Power-Ups timers (وقت انتهاء التفعيل بـ time.time())
power_active = {"double": 0.0, "slow": 0.0, "magnet": 0.0}
power_type = None

SAVE_FILE  = "savegame.txt"
STATS_FILE = "stats.txt"
HIGH_FILE  = "score.txt"

# تحميل High Score
if os.path.exists(HIGH_FILE):
    try:
        with open(HIGH_FILE, "r") as f:
            high_score = int((f.read() or "0").strip())
    except:
        high_score = 0

# إحصاءات عامة
stats = {"games": 0, "total_seconds": 0, "best": high_score}
if os.path.exists(STATS_FILE):
    try:
        with open(STATS_FILE, "r") as f:
            s = (f.read() or "").strip()
            if s:
                g, tot, b = s.split(",")
                stats["games"] = int(g); stats["total_seconds"] = int(tot); stats["best"] = int(b)
    except:
        pass

# =============== الشاشة والخلفيات ===============
wn = turtle.Screen()
wn.title("Snake Galaxy Adventure 🚀")
wn.setup(width=WIDTH, height=HEIGHT)
wn.bgpic("space_bg.gif")      # الخلفية الأساسية
wn.tracer(0)
wn.cv._rootwindow.resizable(True, True)

bg_images = ["space_bg.gif", "space2.gif", "space3.gif"]
bg_images = [p for p in bg_images if os.path.exists(p)]
if not bg_images:
    bg_images = ["space_bg.gif"]

def set_bg_for_level(lv):
    pic = bg_images[(lv-1) % len(bg_images)]
    try:
        wn.bgpic(pic)
    except:
        pass

# نجوم/كواكب تتحرك بالخلفية
planets = []
planet_colors = ["#4B0082", "#8A2BE2", "#7B68EE", "#1E90FF", "#00FFFF"]
for _ in range(8):
    p = turtle.Turtle()
    p.hideturtle(); p.shape("circle"); p.color(random.choice(planet_colors))
    p.penup(); p.speed(0); p.shapesize(random.uniform(2.0, 3.5))
    p.goto(random.randint(-BORDER_X+20, BORDER_X-20), random.randint(-BORDER_Y+20, BORDER_Y-20))
    p.showturtle()
    planets.append(p)

# =============== أقلام النصوص/HUD ===============
pen = turtle.Turtle();       pen.hideturtle();       pen.color("white"); pen.penup();       pen.goto(0, HEIGHT//2 - 40)
level_pen = turtle.Turtle(); level_pen.hideturtle(); level_pen.color("#00FFFF"); level_pen.penup(); level_pen.goto(0, HEIGHT//2 - 70)
title_pen = turtle.Turtle(); title_pen.hideturtle(); title_pen.color("white"); title_pen.penup()
hint_pen  = turtle.Turtle(); hint_pen.hideturtle();  hint_pen.color("#AAAAAA"); hint_pen.penup()

def get_elapsed_text():
    if start_time == 0: return "00:00"
    e = int(time.time() - start_time)
    return f"{e//60:02d}:{e%60:02d}"

def update_hud():
    # Score | High | Time
    pen.clear()
    pen.write(f"Score: {score}  |  High: {high_score}  |  Time: {get_elapsed_text()}",
              align="center", font=("Verdana", 14, "bold"))
    # Level + Power icons
    icons = []
    if power_active["double"] > time.time(): icons.append("🟡x2")
    if power_active["slow"]   > time.time(): icons.append("🔵slow")
    if power_active["magnet"] > time.time(): icons.append("🟣mag")
    level_pen.clear()
    level_pen.write(f"Level: {level}   {'  '.join(icons)}", align="center", font=("Verdana", 10, "bold"))

# =============== عناصر اللعبة ===============
# رأس الثعبان
head = turtle.Turtle()
head.shape("square"); head.color("#00FFFF"); head.shapesize(1.5)
head.penup(); head.goto(0, 0); head.direction = "stop"; head.hideturtle()

# القطع (الجسم)
segments = []

# الطُعم (Glow Orb)
food = turtle.Turtle()
food.shape("circle")
food.color("#FF69B4")    # ابتدائي وردي
food.shapesize(1.8)      # أكبر وواضح
food.penup()
food.goto(0, 100)
food.hideturtle()

# تأثير توهّج للطُعم (تغيير لون دوري)
glow_colors = ["#FF69B4", "#FFB6C1", "#FFD700", "#00FFFF", "#9370DB"]
def animate_food_glow():
    if food.isvisible():
        food.color(random.choice(glow_colors))
    wn.ontimer(animate_food_glow, 200)  # كل 0.2 ثانية
animate_food_glow()

# عوائق (مذنبات)
meteors = []
def spawn_meteors(count=3):
    for m in meteors: m.hideturtle()
    meteors.clear()
    for _ in range(count):
        m = turtle.Turtle()
        m.shape("circle"); m.color("#FF8C00"); m.shapesize(1.6)
        m.penup(); m.speed(0)
        m.goto(random.randint(-BORDER_X+40, BORDER_X-40), random.randint(-BORDER_Y+40, BORDER_Y-40))
        meteors.append(m)

def move_meteors():
    for m in meteors:
        dx = random.choice([-1, 1]) * random.randint(1, 3)
        dy = random.choice([-1, 1]) * random.randint(1, 3)
        m.goto(
            max(min(m.xcor()+dx, BORDER_X-10), -BORDER_X+10),
            max(min(m.ycor()+dy, BORDER_Y-10), -BORDER_Y+10)
        )

# Power-Up واحد يظهر على الخريطة
power_up = turtle.Turtle()
power_up.shape("circle"); power_up.color("gold"); power_up.shapesize(1.2)
power_up.penup(); power_up.hideturtle()

def maybe_spawn_power():
    global power_type
    if power_up.isvisible(): return
    if random.randint(1, 120) == 1:  # احتمال بسيط للظهور
        power_type = random.choice(["double", "slow", "magnet"])
        color_map = {"double":"gold", "slow":"deepskyblue", "magnet":"violet"}
        power_up.color(color_map[power_type])
        power_up.goto(random.randint(-BORDER_X+40, BORDER_X-40),
                      random.randint(-BORDER_Y+40, BORDER_Y-40))
        power_up.showturtle()

def apply_power(ptype, seconds=10):
    power_active[ptype] = time.time() + seconds
    # إظهار نص صغير سريع
    title_pen.goto(0, -HEIGHT//2 + 60)
    title_pen.write(f"{ptype.upper()} ON!", align="center", font=("Verdana", 10, "bold"))
    wn.update(); time.sleep(0.25); title_pen.clear()

# =============== واجهات Splash / Menu / Stats / Over ===============
def draw_splash():
    title_pen.clear(); hint_pen.clear()
    title_pen.goto(0, 60)
    title_pen.write("Ghala Studios Presents", align="center", font=("Verdana", 16, "bold"))
    hint_pen.goto(0, 20)
    hint_pen.write("Preparing Space…", align="center", font=("Verdana", 12, "normal"))

def draw_menu():
    title_pen.clear(); hint_pen.clear()
    set_bg_for_level(1)
    title_pen.goto(0, 80)
    title_pen.write("🚀 Snake Galaxy Adventure 🚀", align="center", font=("Verdana", 18, "bold"))
    title_pen.goto(0, 40)
    title_pen.write("Press ENTER to Start", align="center", font=("Verdana", 12, "normal"))
    title_pen.goto(0, 10)
    title_pen.write("Use W A S D or Arrows to move", align="center", font=("Verdana", 10, "normal"))
    title_pen.goto(0, -20)
    title_pen.write("T: Stats   |   L: Resume (if saved)   |   P: Save   |   Q: Quit",
                    align="center", font=("Verdana", 10, "normal"))

def draw_stats_screen():
    title_pen.clear()
    avg = 0
    if stats["games"] > 0:
        avg = int(stats["total_seconds"]/stats["games"])
    mm, ss = avg//60, avg%60
    title_pen.goto(0, 80)
    title_pen.write("📈 Game Stats", align="center", font=("Verdana", 18, "bold"))
    title_pen.goto(0, 40)
    title_pen.write(f"Total Games Played: {stats['games']}", align="center", font=("Verdana", 12, "normal"))
    title_pen.goto(0, 10)
    title_pen.write(f"Best Score: {stats['best']}", align="center", font=("Verdana", 12, "normal"))
    title_pen.goto(0, -20)
    title_pen.write(f"Average Playtime: {mm:02d}m {ss:02d}s", align="center", font=("Verdana", 12, "normal"))
    title_pen.goto(0, -60)
    title_pen.write("Press M to return to Menu", align="center", font=("Verdana", 11, "normal"))

def draw_game_over():
    title_pen.clear()
    title_pen.goto(0, 70)
    title_pen.write("💀 GAME OVER 💀", align="center", font=("Verdana", 20, "bold"))
    title_pen.goto(0, 30)
    title_pen.write(f"Final Score: {score}", align="center", font=("Verdana", 13, "normal"))
    title_pen.goto(0, 0)
    title_pen.write(f"High Score: {high_score}", align="center", font=("Verdana", 12, "bold"))
    title_pen.goto(0, -30)
    title_pen.write(f"Level Reached: {level}", align="center", font=("Verdana", 11, "normal"))
    title_pen.goto(0, -60)
    title_pen.write(f"Foods Eaten: {foods_eaten}", align="center", font=("Verdana", 11, "normal"))
    title_pen.goto(0, -90)
    title_pen.write(f"Total Play Time: {get_elapsed_text()}", align="center", font=("Verdana", 11, "normal"))
    title_pen.goto(0, -130)
    title_pen.write("Press ENTER to Restart   |   M: Menu   |   Q: Quit",
                    align="center", font=("Verdana", 11, "normal"))
    play_sound("over.wav")

# =============== تحكم واتجاهات ===============
def goup():    # لأعلى
    if head.direction != "down": head.direction = "up"
def godown():  # لأسفل
    if head.direction != "up": head.direction = "down"
def goleft():  # يسار
    if head.direction != "right": head.direction = "left"
def goright(): # يمين
    if head.direction != "left": head.direction = "right"

def move():
    step = 20
    # تأثير Slow Motion: يزيد التأخير الفعلي
    effective_delay = delay
    if power_active["slow"] > time.time():
        effective_delay = min(0.12, delay + 0.03)

    if head.direction == "up":    head.sety(head.ycor() + step)
    if head.direction == "down":  head.sety(head.ycor() - step)
    if head.direction == "left":  head.setx(head.xcor() - step)
    if head.direction == "right": head.setx(head.xcor() + step)
    if head.direction != "stop":  play_sound("move.wav")
    return effective_delay

# =============== إدارة اللعبة (بدء/انتهاء/حفظ) ===============
def reset_snake():
    head.goto(0, 0); head.direction = "stop"
    for s in segments: s.hideturtle()
    segments.clear()

def start_game(from_save=False):
    global game_state, score, level, delay, start_time, foods_eaten, last_eat_times, power_active
    game_state = STATE_PLAY
    play_sound("start.wav")
    score = 0; level = 1; delay = 0.08
    start_time = time.time(); foods_eaten = 0; last_eat_times = []
    power_active = {"double":0.0, "slow":0.0, "magnet":0.0}

    title_pen.clear()
    head.showturtle(); food.showturtle()
    reset_snake()
    set_bg_for_level(level)
    spawn_meteors(3)
    update_hud()

    if from_save and os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                sx, sy, fx, fy, sc, lv = f.read().strip().split(",")
            head.goto(float(sx), float(sy)); food.goto(float(fx), float(fy))
            # استعادة نقاط/مستوى
            globals()["score"] = int(sc)
            globals()["level"] = int(lv)
            set_bg_for_level(level)
            update_hud()
        except:
            pass

def save_game():
    try:
        with open(SAVE_FILE, "w") as f:
            f.write(f"{head.xcor()},{head.ycor()},{food.xcor()},{food.ycor()},{score},{level}")
    except:
        pass

def resume_from_save():
    if os.path.exists(SAVE_FILE):
        start_game(from_save=True)

def to_menu():
    global game_state
    game_state = STATE_MENU
    draw_menu()

def to_stats():
    global game_state
    game_state = STATE_STATS
    draw_stats_screen()

def game_over():
    global game_state, high_score, stats
    game_state = STATE_OVER
    head.hideturtle(); food.hideturtle()

    # High Score
    if score > high_score:
        high_score = score
        with open(HIGH_FILE, "w") as f: f.write(str(high_score))

    # إحصاءات عامة
    stats["games"] += 1
    if start_time:
        stats["total_seconds"] += int(time.time() - start_time)
    stats["best"] = max(stats["best"], high_score)
    try:
        with open(STATS_FILE, "w") as f:
            f.write(f"{stats['games']},{stats['total_seconds']},{stats['best']}")
    except:
        pass

    draw_game_over()

# =============== ربط المفاتيح ===============
wn.listen()
# البدء/الإعادة
wn.onkeypress(lambda: start_game(False), "Return")
# قائمة/إحصاءات/خروج/حفظ/تحميل
wn.onkeypress(to_menu, "m")
wn.onkeypress(to_stats, "t")
wn.onkeypress(lambda: wn.bye(), "q")
wn.onkeypress(save_game, "p")
wn.onkeypress(resume_from_save, "l")
# حركة: WASD + الأسهم
wn.onkeypress(goup, "w");    wn.onkeypress(godown, "s")
wn.onkeypress(goleft, "a");  wn.onkeypress(goright, "d")
wn.onkeypress(goup, "Up");   wn.onkeypress(godown, "Down")
wn.onkeypress(goleft, "Left"); wn.onkeypress(goright, "Right")

# =============== Splash أولية ثم القائمة ===============
draw_splash()
splash_start = time.time()

# =============== الحلقة الرئيسية ===============
while True:
    wn.update()

    # حركة النجوم بالخلفية
    for p in planets:
        p.sety(p.ycor() - 1.2)
        if p.ycor() < -BORDER_Y:
            p.goto(random.randint(-BORDER_X+20, BORDER_X-20), BORDER_Y)

    # انتقال تلقائي من Splash إلى Menu بعد 1.5 ثانية
    if game_state == STATE_SPLASH and time.time() - splash_start >= 1.5:
        game_state = STATE_MENU
        draw_menu()

    if game_state == STATE_PLAY:
        move_meteors()

        # تحريك الجسم (ذيل ← رأس)
        for i in range(len(segments)-1, 0, -1):
            segments[i].goto(segments[i-1].xcor(), segments[i-1].ycor())
        if segments:
            segments[0].goto(head.xcor(), head.ycor())

        # حركة الرأس + تأخير فعلي
        effective_delay = move()

        # حدود الملعب
        if abs(head.xcor()) > BORDER_X or abs(head.ycor()) > BORDER_Y:
            game_over(); continue

        # اصطدام بالمذنبات
        for m in meteors:
            if head.distance(m) < 20:
                game_over(); break
        if game_state == STATE_OVER:
            continue

        # مغناطيس: يجذب الطعام إذا قريب
        if power_active["magnet"] > time.time():
            if head.distance(food) < 120:
                fx, fy = food.xcor(), food.ycor()
                hx, hy = head.xcor(), head.ycor()
                food.goto(fx + (hx-fx)*0.2, fy + (hy-fy)*0.2)

        # التقاط الطُعم
        if head.distance(food) < 25:
            play_sound("eat.wav")
            foods_eaten += 1

            # Combo: 3 طُعُم خلال 10 ثوانٍ → +20
            now = time.time()
            last_eat_times[:] = [t for t in last_eat_times if now - t <= COMBO_WINDOW_S]
            last_eat_times.append(now)
            bonus = 20 if len(last_eat_times) >= 3 else 0

            # نقل الطُعم + لون جديد
            food.goto(random.randint(-BORDER_X+40, BORDER_X-40),
                      random.randint(-BORDER_Y+40, BORDER_Y-40))
            food.color(random.choice(glow_colors))

            # إضافة قطعة للجسم
            seg = turtle.Turtle()
            seg.shape("square"); seg.color("#33FFFF"); seg.shapesize(1.2)
            seg.penup(); seg.speed(0)
            segments.append(seg)

            # بريق سريع
            head.color("#FFFFFF"); wn.update(); time.sleep(0.05); head.color("#00FFFF")

            # نقاط (ومضاعفة إذا Double فعّال)
            gain = 10 + bonus
            if power_active["double"] > time.time():
                gain *= 2
            score += gain

            # مستوى كل 50 نقطة
            old_level = level
            level = max(1, 1 + score // 50)
            if level != old_level:
                delay = max(0.03, 0.08 - 0.01*(level-1))
                set_bg_for_level(level)
                spawn_meteors(min(6, 2 + level))  # أكثر عوائق مع المستويات
                play_sound("levelup.wav")

            update_hud()
            maybe_spawn_power()

        # التقاط Power-Up
        if power_up.isvisible() and head.distance(power_up) < 22:
            play_sound("eat.wav")
            pt = power_type
            power_up.hideturtle()
            apply_power(pt, seconds=10)

        # High Score
        if score > high_score:
            high_score = score
            with open(HIGH_FILE, "w") as f: f.write(str(high_score))

        time.sleep(effective_delay)

    elif game_state in (STATE_MENU, STATE_OVER, STATE_STATS):
        # بانتظار إدخال من اللاعب
        pass
