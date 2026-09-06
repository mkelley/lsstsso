import lsstsso

comets = lsstsso.get.comets()
comets.sort("designation")
print(comets)
