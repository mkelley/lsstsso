from lsstsso import RSP, get

rsp = RSP()
comets = get.comets(rsp)
comets.sort("designation")
print(comets)
