from art import _back_bough as BB, _back_rice as BR, _back_emblem as BE, _back_geo as BG
BB.BOUGH["lenspar"]=dict(c=(181.8,525.0), radii=(258,284,310,336,362,388,414), sweep=80)
BB.BOUGH["tick"]=dict(tick=12.0, angle=45.0, pitch=9.8)
BB.BOUGH["pieces"]=True; BB.BOUGH["min_piece"]=40
BB.BOUGH["left"]=[]
BB.BOUGH["y_base"]=300.0
BR.SHEAF["culm"]["way"]=[(172.0, 240.0), (188.0, 262.0), (198.0, 285.0), (226.0, 304.0), (262.0, 322.0), (300.0, 338.0), (330.0, 349.0), (352.0, 355.0)]
BR.SHEAF["culm"]["panicle_len"]=170.0
BR.SHEAF["culm"]["panicle"]=dict(n_female=9, n_male=4, m_pitch=14.0)
