from rv import *
from deck.motifs import *
from deck import frames
club = frames.ace_pip_d('C')
st = rice_stalk(375, 560, -90, 190, w=T.MEDIUM)
save(reversed_out(club, st, color=T.INK), "ace_club_stalk_ko_zoom", view=(345,360,405,440), zoom=10, pad=0)
