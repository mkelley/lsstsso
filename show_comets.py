from lsstsso import RSP, get

rsp = RSP()
comets = get.comets(rsp)
comets.sort("designation")
comets.as_table().pprint_all()
