_qf = QF.queen_face
def _qf2(*a, **k):
    k.setdefault('far_low', 0.72)
    return _qf(*a, **k)
QF = type('QFmod', (), {'queen_face': staticmethod(_qf2)})
