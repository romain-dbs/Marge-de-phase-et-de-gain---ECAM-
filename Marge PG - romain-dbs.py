"""Diagrammes de Bode : trouvez la marge de gain et la marge de phase.

Installation : pip install numpy matplotlib
Lancement    : python bode_marges.py

- Passez la souris sur un diagramme : curseur synchronisé (pulsation, gain, phase).
- Tapez un gain ou une phase dans « Aller au… » : le curseur s'y place.
- Tapez vos marges dans les cases (Entrée ou bouton Vérifier).
- Le bouton ↻ génère un nouveau diagramme, Révéler affiche la solution.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button

TOL_G, TOL_P = 1.0, 3.0  # tolérances : dB et degrés
DARK = True  # True = thème sombre (comme la version web), False = thème clair

# Palette identique à la version web
if DARK:
    BG, FG, MUT, GRID, C1, C2, CUR, OK, KO, CARD = ("#0f1620", "#e6edf5", "#8a99ab", "#26313f", "#5aaaf0",
                                                  "#f0955a", "#ff6b86", "#4cc789", "#ff7b6b", "#17202c")
else:
    BG, FG, MUT, GRID, C1, C2, CUR, OK, KO, CARD = ("#f5f7fa", "#14202e", "#6b7a8c", "#dde3ea", "#1f6fb2",
                                                  "#c2571a", "#d12f4a", "#1d8a4e", "#c0392b", "#ffffff")


def gen():
    p1 = 10 ** np.random.uniform(-.5, .7)
    p2 = p1 * 10 ** np.random.uniform(.2, .9)
    p3 = p2 * 10 ** np.random.uniform(.2, .9)
    return 10 ** np.random.uniform(.5, 1.6), [p1, p2, p3]


def gain(K, P, w):
    return 20 * np.log10(K / np.prod([np.sqrt(1 + (w / p) ** 2) for p in P], axis=0))


def phase(P, w):
    return -sum(np.degrees(np.arctan(w / p)) for p in P)


def root(f, a, b):
    for _ in range(60):
        m = np.sqrt(a * b)
        if f(a) * f(m) <= 0:
            b = m
        else:
            a = m
    return np.sqrt(a * b)


class App:
    def __init__(self):
        self.fig, (self.ag, self.ap) = plt.subplots(2, 1, sharex=True, figsize=(10, 8), facecolor=BG)
        self.fig.subplots_adjust(bottom=0.27, hspace=0.12, left=0.09, right=0.97, top=0.95)
        self.fig.canvas.manager.set_window_title("Marges de gain et de phase")
        self.info = self.fig.text(0.09, 0.215, "", fontsize=10, family="monospace", color=FG,
                                bbox=dict(boxstyle="round,pad=0.4", fc=CARD, ec=GRID))
        self.fb = self.fig.text(0.09, 0.18, "", fontsize=11, weight="bold", color=FG)
        self.tg = self.box([0.20, 0.03, 0.10, 0.045], "Marge de gain (dB) ")
        self.tp = self.box([0.50, 0.03, 0.10, 0.045], "Marge de phase (°) ")
        self.bv = self.btn([0.64, 0.03, 0.09, 0.045], "Vérifier", "primary")
        self.br = self.btn([0.74, 0.03, 0.09, 0.045], "Révéler", "outline")
        self.bn = self.btn([0.88, 0.03, 0.07, 0.045], "↻", "icon")
        self.vg = self.box([0.20, 0.10, 0.10, 0.045], "Aller au gain (dB) ")
        self.vp = self.box([0.50, 0.10, 0.10, 0.045], "Aller à la phase (°) ")
        self.vg.on_submit(lambda t: self.aller(t, True))
        self.vp.on_submit(lambda t: self.aller(t, False))
        self.bv.on_clicked(lambda e: self.check())
        self.br.on_clicked(lambda e: self.reveal())
        self.bn.on_clicked(lambda e: self.new())
        self.tg.on_submit(lambda t: self.check())
        self.tp.on_submit(lambda t: self.check())
        self.fig.canvas.mpl_connect("motion_notify_event", self.move)
        self.new()

    def box(self, rect, label):
        ax = self.fig.add_axes(rect)
        tb = TextBox(ax, label, color=CARD, hovercolor=CARD)
        tb.label.set_color(MUT)
        tb.text_disp.set_color(FG)
        for sp in ax.spines.values():
            sp.set_edgecolor(GRID)
        return tb

    def btn(self, rect, label, kind):
        ax = self.fig.add_axes(rect)
        b = Button(ax, label, color=C1 if kind == "primary" else CARD,
                   hovercolor=C1 if kind == "primary" else GRID)
        b.label.set_color("white" if kind == "primary" else (FG if kind == "icon" else C1))
        if kind == "icon":
            b.label.set_fontsize(16)
        for sp in ax.spines.values():
            sp.set_edgecolor(GRID if kind == "icon" else C1)
        return b

    def new(self):
        self.K, self.P = gen()
        lo, hi = self.P[0] / 100, self.P[2] * 100
        self.w = np.logspace(np.log10(lo), np.log10(hi), 600)
        self.wc = root(lambda w: gain(self.K, self.P, w), lo, hi)
        self.wpc = root(lambda w: phase(self.P, w) + 180, lo, hi)
        self.GM = -gain(self.K, self.P, self.wpc)
        self.PM = 180 + phase(self.P, self.wc)
        self.tg.set_val("")
        self.tp.set_val("")
        self.vg.set_val("")
        self.vp.set_val("")
        self.fb.set_text("")
        self.info.set_text("Passez la souris sur un diagramme pour lire les valeurs.")
        self.draw()

    def draw(self):
        g, p = self.ag, self.ap
        g.clear(); p.clear()
        g.semilogx(self.w, gain(self.K, self.P, self.w), color=C1, lw=2.2)
        p.semilogx(self.w, phase(self.P, self.w), color=C2, lw=2.2)
        g.axhline(0, color=FG, lw=1.2); p.axhline(-180, color=FG, lw=1.2)
        g.set_ylabel("Gain (dB)"); p.set_ylabel("Phase (°)"); p.set_xlabel("ω (rad/s)")
        p.set_yticks(range(-270, 1, 45))
        for a in (g, p):
            a.set_facecolor(CARD)
            a.grid(True, which="both", color=GRID, lw=.8)
            a.tick_params(colors=MUT)
            a.xaxis.label.set_color(MUT)
            a.yaxis.label.set_color(MUT)
            for sp in a.spines.values():
                sp.set_edgecolor(GRID)
        g.set_title("Marges de gain et de phase", color=FG, fontsize=13)
        self.vl = [a.axvline(self.w[0], color=CUR, lw=1, visible=False) for a in (g, p)]
        self.dots = [a.plot([], [], "o", color=CUR)[0] for a in (g, p)]
        self.fig.canvas.draw_idle()

    def move(self, e):
        if e.inaxes not in (self.ag, self.ap) or e.xdata is None:
            return
        self.place(e.xdata)

    def place(self, w):
        gv, pv = gain(self.K, self.P, w), phase(self.P, w)
        for v in self.vl:
            v.set_xdata([w, w]); v.set_visible(True)
        self.dots[0].set_data([w], [gv]); self.dots[1].set_data([w], [pv])
        self.info.set_text(f"ω = {w:8.3f} rad/s | Gain = {gv:7.2f} dB | Phase = {pv:8.2f}°")
        self.fig.canvas.draw_idle()

    def aller(self, txt, is_gain):
        try:
            v = float(txt.replace(",", "."))
        except ValueError:
            return
        lo, hi = self.w[0], self.w[-1]
        f = (lambda w: gain(self.K, self.P, w)) if is_gain else (lambda w: phase(self.P, w))
        if (f(lo) - v) * (f(hi) - v) > 0:
            self.info.set_text(f"Valeur hors du diagramme (de {f(hi):.1f} à {f(lo):.1f}).")
            self.fig.canvas.draw_idle()
            return
        self.place(root(lambda w: f(w) - v, lo, hi))

    def check(self):
        try:
            a = float(self.tg.text.replace(",", "."))
            b = float(self.tp.text.replace(",", "."))
        except ValueError:
            self.fb.set_color(KO); self.fb.set_text("Saisissez les deux marges (nombres).")
            self.fig.canvas.draw_idle(); return
        og, op = abs(a - self.GM) <= TOL_G, abs(b - self.PM) <= TOL_P
        if og and op:
            msg = "Bravo, les deux marges sont justes."
        elif og:
            msg = "Marge de gain juste, marge de phase incorrecte."
        elif op:
            msg = "Marge de phase juste, marge de gain incorrecte."
        else:
            msg = "Les deux marges sont incorrectes, regardez encore."
        self.fb.set_color(OK if og and op else KO)
        self.fb.set_text(msg)
        self.fig.canvas.draw_idle()

    def reveal(self):
        g, p = self.ag, self.ap
        gp = gain(self.K, self.P, self.wpc)
        pc = phase(self.P, self.wc)
        g.vlines(self.wpc, 0, gp, color=OK, ls="--")
        g.annotate(f"MG = {self.GM:.2f} dB", (self.wpc, gp / 2), color=OK)
        p.vlines(self.wc, -180, pc, color=OK, ls="--")
        p.annotate(f"MP = {self.PM:.2f}°", (self.wc, (pc - 180) / 2), color=OK)
        self.fb.set_color(FG)
        self.fb.set_text(f"MG = {self.GM:.2f} dB (ω = {self.wpc:.2f})   MP = {self.PM:.2f}° (ω = {self.wc:.2f})")
        self.fig.canvas.draw_idle()


if __name__ == "__main__":
    app = App()
    plt.show()
