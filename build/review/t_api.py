from rv import *
from deck.motifs import *
import traceback
def t(name, fn):
    try:
        f = fn(); print("OK ", name, repr(f)[:80], f.meta.get("warnings"))
        return f
    except Exception as e:
        print("ERR", name, type(e).__name__, str(e)[:200])
t("rice_wreath d-string", lambda: rice_wreath("M375 700 A 150 150 0 0 0 505 625"))
t("comb_spray d-string arc", lambda: comb_spray("M375 250 A 200 200 0 0 1 420 118", cone=11))
t("gill_plume points", lambda: gill_plume([(0,0),(10,-20),(15,-40)]))
t("current_lines 3", lambda: current_lines("M0 0 C 20 40 20 80 60 110", 3))
t("lion_mark 24", lambda: lion_mark(0,0,24))
t("lion_mark 70 (>60)", lambda: lion_mark(0,0,70))
t("fault_plinth", lambda: fault_plinth(375, 91.5, 60, hatch_step=0))
t("bubble_triad ring", lambda: bubble_triad(0,0,-45,(6,10,6),style="ring"))
t("pearl_beading arc", lambda: pearl_beading("M150 300 A 200 200 0 0 1 600 300"))
t("stepping_stones divider", lambda: stepping_stones(139, 611, 525, band=10, pitch=40, stone=(10,6), centre=None))
t("reed_ladder side", lambda: reed_ladder((68.5, 106), (68.5, 944), width=22, rails=False))
t("festoon", lambda: festoon([(180, 380), (300, 380), (420, 392)], sag=22))
t("tooled_scroll 28", lambda: tooled_scroll(0, 200, 0, height=28))
t("strata fault", lambda: strata("M300 330 L460 330 L460 500 L300 500 Z", fault=((300, 480), (420, 330))))
t("scale_lattice r5", lambda: scale_lattice("M0 0 L100 0 L100 100 L0 100 Z", r=5))
t("stalactite rot", lambda: stalactite(0,0, rot=30))
t("knee_crenellation", lambda: knee_crenellation(290, 460, 150, h=50))
t("rowel solid", lambda: rowel_star(0,0,12, solid=True, color=T.FOIL))
t("vent_roundel", lambda: vent_roundel(68.5, 74.5))
t("lens_field", lambda: lens_field(lens_geometry(), corners=[(37.5,37.5),(712.5,37.5),(37.5,1012.5),(712.5,1012.5)]))
t("blind_salamander rot", lambda: blind_salamander(0,0,rot=45))
t("lion_andante", lambda: lion_andante(384.5, 540))
t("spring_vent", lambda: spring_vent())
t("frag scale reject", lambda: source_rosette(0,0,16).transformed((2,0,0,2,0,0)))
t("frag shear accepted?", lambda: source_rosette(0,0,16).transformed((1,0,0.5,1,0,0)))
