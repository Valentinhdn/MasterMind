"""
MasterMind - PySide6 polished UI

Run:
    pip install PySide6
    python mastermind_python_gui.py

Features:
- Game-like visual (gradients, shadows, smooth buttons)
- Click to select slot, click palette to place color
- Keyboard shortcuts: 1..6 to place, Enter to submit, Backspace to erase
- Animated feedback (simple scale animation on placement)
- History, hints, new game, give up
- Configurable colors, slots, rows

This is a single-file implementation using PySide6. It draws the board with custom painting to achieve a nicer visual than simple Tkinter widgets.
"""

from PySide6.QtCore import Qt, QRectF, QPointF, QEasingCurve, QPropertyAnimation, QObject, Property, QTimer
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGridLayout,
    QFrame,
    QMainWindow,
    QSizePolicy,
    QMessageBox,
)
import random
import sys

# Configuration
DEFAULT_COLORS = [
    "#EF476F",  # rose
    "#FFD166",  # jaune
    "#06D6A0",  # vert
    "#118AB2",  # bleu
    "#6A4C93",  # violet
    "#FF9F1C",  # orange
]
SLOTS = 4
MAX_ROWS = 10


def random_code(colors, length):
    return [random.choice(colors) for _ in range(length)]


def score_guess(secret, guess):
    secret_copy = list(secret)
    guess_copy = list(guess)
    black = 0
    for i in range(len(secret_copy)):
        if guess_copy[i] is not None and secret_copy[i] == guess_copy[i]:
            black += 1
            secret_copy[i] = None
            guess_copy[i] = None
    white = 0
    for i in range(len(guess_copy)):
        if guess_copy[i] is None:
            continue
        try:
            idx = secret_copy.index(guess_copy[i])
            white += 1
            secret_copy[idx] = None
        except ValueError:
            pass
    return black, white


class AnimatedObject(QObject):
    def __init__(self):
        super().__init__()
        self._scale = 1.0

    def _get(self):
        return self._scale

    def _set(self, v):
        self._scale = v

    scale = Property(float, _get, _set)


class BoardWidget(QWidget):
    def __init__(self, colors, slots=SLOTS, rows=MAX_ROWS, parent=None):
        super().__init__(parent)
        self.colors = colors
        self.slots = slots
        self.rows = rows
        self.board = [[None for _ in range(self.slots)] for _ in range(self.rows)]
        self.history = [None for _ in range(self.rows)]
        self.row_index = 0
        self.selected_slot = 0
        self.secret = random_code(self.colors, self.slots)
        self.finished = False
        self.anim = AnimatedObject()
        self.scale_animation = None
        self.message = ""
        self.setMinimumWidth(640)
        self.setMinimumHeight(720)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def reset(self):
        self.board = [[None for _ in range(self.slots)] for _ in range(self.rows)]
        self.history = [None for _ in range(self.rows)]
        self.row_index = 0
        self.selected_slot = 0
        self.secret = random_code(self.colors, self.slots)
        self.finished = False
        self.message = "Nouvelle partie — bonne chance !"
        self.update()

    def give_up(self):
        self.finished = True
        self.message = f"Tu as abandonné. La combinaison était: "
        self.update()

    def place_color(self, color):
        if self.finished:
            return
        self.board[self.row_index][self.selected_slot] = color
        # animate
        self.play_pop_animation()
        # advance slot
        self.selected_slot = (self.selected_slot + 1) % self.slots
        self.update()

    def remove_color(self, slot=None):
        if slot is None:
            slot = (self.selected_slot - 1) % self.slots
        self.board[self.row_index][slot] = None
        self.selected_slot = slot
        self.update()

    def submit_row(self):
        if self.finished:
            return
        guess = self.board[self.row_index]
        if any(c is None for c in guess):
            self.message = "Remplis toutes les couleurs avant de valider."
            self.update()
            return
        black, white = score_guess(self.secret, guess)
        self.history[self.row_index] = {"black": black, "white": white, "guess": list(guess)}
        if black == self.slots:
            self.finished = True
            self.message = f"Bravo ! Tu as trouvé la combinaison en {self.row_index + 1} essai(s) 🎉"
            self.update()
            return
        self.row_index += 1
        if self.row_index >= self.rows:
            self.finished = True
            self.message = f"Partie terminée — la combinaison était:"
            self.update()
            return
        self.selected_slot = 0
        self.message = "Essai soumis. Continue !"
        self.update()

    def reveal_hint(self):
        if self.finished:
            return
        idx = random.randrange(self.slots)
        col = self.secret[idx]
        self.message = f"Indice: la position {idx + 1} contient →"
        self.hint_color = col
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        # background gradient
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, QColor("#0f1724"))
        grad.setColorAt(1, QColor("#071124"))
        p.fillRect(self.rect(), grad)

        margin = 24
        board_w = self.width() - margin * 2
        row_h = (self.height() - 200) / self.rows
        peg_size = min(64, int(row_h * 0.6))
        gap = int((board_w - (self.slots * peg_size)) / (self.slots + 1)) if self.slots else 10
        left = margin
        top = 40

        font = QFont("Segoe UI", 10)
        p.setFont(font)

        for r in range(self.rows):
            y = top + r * row_h
            # row background (glass card)
            rect = QRectF(left, y + 6, board_w, row_h - 12)
            card_grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
            card_grad.setColorAt(0, QColor(255, 255, 255, 18))
            card_grad.setColorAt(1, QColor(255, 255, 255, 6))
            p.setBrush(QBrush(card_grad))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(rect, 12, 12)

            # draw pegs
            for s in range(self.slots):
                x = left + gap + s * (peg_size + gap)
                center = QPointF(x + peg_size / 2, y + row_h / 2)
                color = self.board[r][s]
                is_active = (r == self.row_index and not self.finished)
                ring = (self.selected_slot == s and is_active)

                # draw outer shadow / ring
                if ring:
                    shadow_rad = peg_size * 0.6
                    p.setBrush(Qt.NoBrush)
                    pen = QPen(QColor(34, 197, 94, 120))
                    pen.setWidth(6)
                    p.setPen(pen)
                    p.drawEllipse(center, shadow_rad, shadow_rad)

                # peg background
                peg_rect = QRectF(x, y + (row_h - peg_size) / 2, peg_size, peg_size)
                if color:
                    # colored peg with glossy gradient
                    c = QColor(color)
                    peg_grad = QLinearGradient(peg_rect.topLeft(), peg_rect.bottomRight())
                    peg_grad.setColorAt(0, c.lighter(120))
                    peg_grad.setColorAt(1, c.darker(120))
                    p.setBrush(QBrush(peg_grad))
                    p.setPen(QPen(QColor(255, 255, 255, 60), 1))
                    p.drawEllipse(peg_rect)
                    # small highlight
                    highlight = QRectF(peg_rect.x() + peg_size * 0.18, peg_rect.y() + peg_size * 0.12, peg_size * 0.28, peg_size * 0.18)
                    p.setBrush(QBrush(QColor(255, 255, 255, 120)))
                    p.setPen(Qt.NoPen)
                    p.drawEllipse(highlight)
                else:
                    # empty peg
                    p.setBrush(QBrush(QColor(255, 255, 255, 8)))
                    p.setPen(QPen(QColor(255, 255, 255, 30), 1))
                    p.drawEllipse(peg_rect)
                    inner = QRectF(peg_rect.x() + peg_size * 0.35, peg_rect.y() + peg_size * 0.35, peg_size * 0.3, peg_size * 0.3)
                    p.setBrush(QBrush(QColor(255, 255, 255, 12)))
                    p.drawEllipse(inner)

            # draw feedback (black/white small dots) on the right
            feedback_x = left + board_w - 120
            fb_size = 8
            stats = self.history[r]
            if stats:
                bx = feedback_x
                by = y + row_h / 2 - fb_size
                # draw black pegs
                for i in range(stats['black']):
                    rect = QRectF(bx + i * (fb_size + 4), by, fb_size, fb_size)
                    p.setBrush(QColor('#00FF88'))
                    p.setPen(QPen(QColor(255, 255, 255, 20), 1))
                    p.drawEllipse(rect)
                # draw white pegs
                for i in range(stats['white']):
                    rect = QRectF(bx + (i + stats['black']) * (fb_size + 4), by, fb_size, fb_size)
                    p.setBrush(QColor('#FFFF88'))
                    p.setPen(QPen(QColor(0, 0, 0, 20), 1))
                    p.drawEllipse(rect)

            # row text
            p.setPen(QColor(255, 255, 255, 140))
            p.drawText(QRectF(left + 8, y + 8, 100, 20), f"Essai {r + 1}")

        # message area
        p.setPen(QColor(255, 255, 255, 200))
        p.setFont(QFont("Segoe UI", 11))
        p.drawText(QRectF(left, self.height() - 110, board_w, 24), Qt.AlignLeft, self.message)
        if self.finished:
            x0 = 30; y0 = self.height()-50; size=30
            for i,c in enumerate(self.secret):
                p.setBrush(QColor(c))
                p.setPen(QPen(Qt.white,1))
                p.drawEllipse(QRectF(x0+i*(size+10),y0,size,size))
        
        # affichage message
        # p.drawText(30, self.height() - 80, self.message)

        # 🔽 si un indice est actif, on affiche la couleur correspondante
        if hasattr(self, 'hint_color') and self.hint_color and not self.finished:
            p.setBrush(QColor(self.hint_color))
            p.setPen(QPen(Qt.white, 1))
            p.drawEllipse(QRectF(400, self.height() - 100, 30, 30))


    def play_pop_animation(self):
        if self.scale_animation:
            self.scale_animation.stop()
        self.scale_animation = QPropertyAnimation(self.anim, b"scale")
        self.scale_animation.setDuration(240)
        self.scale_animation.setStartValue(1.0)
        self.scale_animation.setKeyValueAt(0.5, 1.12)
        self.scale_animation.setEndValue(1.0)
        self.scale_animation.setEasingCurve(QEasingCurve.OutBack)
        self.scale_animation.start()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MasterMind — PySide6 Pro UI")
        self.colors = DEFAULT_COLORS
        self.slots = SLOTS
        self.rows = MAX_ROWS
        self.board_widget = BoardWidget(self.colors, self.slots, self.rows)
        self.init_ui()
        self.installEventFilter(self)

    def init_ui(self):
        main = QWidget()
        root = QHBoxLayout()
        main.setLayout(root)

        # left: board
        left_frame = QVBoxLayout()
        left_frame.addWidget(self.board_widget)

        btn_row = QHBoxLayout()
        btn_new = QPushButton("Nouvelle partie")
        btn_new.clicked.connect(self.new_game)
        btn_valid = QPushButton("Valider (Entrée)")
        btn_valid.clicked.connect(self.board_widget.submit_row)
        btn_hint = QPushButton("Indice")
        btn_hint.clicked.connect(self.board_widget.reveal_hint)
        btn_giveup = QPushButton("Abandonner")
        btn_giveup.clicked.connect(self.board_widget.give_up)
        btn_row.addWidget(btn_new)
        btn_row.addWidget(btn_valid)
        btn_row.addWidget(btn_hint)
        btn_row.addWidget(btn_giveup)

        left_frame.addLayout(btn_row)

        root.addLayout(left_frame, 3)

        # right: palette + info
        right = QVBoxLayout()
        pal_label = QLabel("Palette")
        pal_label.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        right.addWidget(pal_label)

        grid = QGridLayout()
        grid.setSpacing(8)
        for i, c in enumerate(self.colors):
            btn = QPushButton(str(i + 1))
            btn.setFixedSize(96, 48)
            btn.setStyleSheet(self.palette_button_style(c))
            btn.clicked.connect(lambda checked, col=c: self.on_palette_click(col))
            grid.addWidget(btn, i // 2, i % 2)
        right.addLayout(grid)

        info = QLabel("Raccourcis: touches 1–6 pour choisir, Entrée=valider, Backspace=supprimer")
        info.setWordWrap(True)
        info.setStyleSheet("color: #cbd5e1; font-size: 11px")
        right.addWidget(info)

        status_box = QFrame()
        status_box.setFrameShape(QFrame.StyledPanel)
        status_box.setStyleSheet("background: rgba(255,255,255,8%); border-radius: 10px; padding: 10px;")
        status_layout = QVBoxLayout()
        status_box.setLayout(status_layout)
        self.status_label = QLabel(f"Essai actuel: {self.board_widget.row_index + 1}/{self.rows}")
        status_layout.addWidget(self.status_label)

        right.addWidget(status_box)

        hist_label = QLabel("Historique (récent)")
        hist_label.setFont(QFont("Segoe UI", 11))
        right.addWidget(hist_label)
        self.hist_area = QVBoxLayout()
        right.addLayout(self.hist_area)
        self.update_history_display()

        right.addStretch()
        root.addLayout(right, 1)

        self.setCentralWidget(main)
        self.setMinimumSize(1000, 720)
        # periodic UI update timer
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.ui_tick)
        self.ui_timer.start(150)

    def palette_button_style(self, color):
        return f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {color}, stop:1 {color}); color: white; border-radius: 10px; font-weight: 700;"

    def on_palette_click(self, color):
        self.board_widget.place_color(color)
        self.update_status()
        self.update_history_display()

    def new_game(self):
        self.board_widget.reset()
        self.update_status()
        self.update_history_display()

    def update_history_display(self):
        # clear
        while self.hist_area.count():
            item = self.hist_area.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # add recent history (up to current row)
        for idx in range(0, self.board_widget.row_index + 1):
            h = self.board_widget.history[idx]
            row_w = QWidget()
            row_l = QHBoxLayout()
            row_w.setLayout(row_l)
            if h:
                for g in h['guess']:
                    sw = QLabel()
                    sw.setFixedSize(18, 18)
                    sw.setStyleSheet(f"background: {g}; border-radius: 9px; border: 1px solid rgba(0,0,0,0.2);")
                    row_l.addWidget(sw)
                lab = QLabel(f"  {h['black']} ● {h['white']} ○")
                lab.setStyleSheet("color: #cbd5e1")
                row_l.addWidget(lab)
            else:
                row_l.addWidget(QLabel("—"))
            self.hist_area.addWidget(row_w)

    def update_status(self):
        self.status_label.setText(f"Essai actuel: {self.board_widget.row_index + 1}/{self.rows}")

    def ui_tick(self):
        # update labels and repaint board
        self.update_status()
        self.update_history_display()
        self.board_widget.update()

    def keyPressEvent(self, event):
        k = event.key()
        if Qt.Key_1 <= k <= Qt.Key_9:
            idx = k - Qt.Key_1
            if idx < len(self.colors):
                self.board_widget.place_color(self.colors[idx])
                return
        if k == Qt.Key_Return or k == Qt.Key_Enter:
            self.board_widget.submit_row()
            return
        if k == Qt.Key_Backspace:
            self.board_widget.remove_color()
            return
        # navigation
        if k == Qt.Key_Left:
            self.board_widget.selected_slot = max(0, self.board_widget.selected_slot - 1)
            return
        if k == Qt.Key_Right:
            self.board_widget.selected_slot = min(self.slots - 1, self.board_widget.selected_slot + 1)
            return


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
