import numpy as np
import matplotlib.pyplot as plt

class Einzugsgebiet:
    def __init__(self, name, fläche, gebäude_liste):
        self.name = name
        self.fläche = fläche
        self.gebäude_liste = gebäude_liste
        self.anzahl_gebäude = len(gebäude_liste)
        self.anzahl_WG = Einzugsgebiet.anzahl_Wohngebäude(self)
        self.anzahl_NWG = self.anzahl_gebäude - self.anzahl_WG
        self.endenergie_heizen = Einzugsgebiet.heizenergie(self)
        self.endenergie_kühlen = Einzugsgebiet.kühlenergie(self)
        self.energieverlauf_plt, self.ax = plt.subplots()
        self.ax.plot(self.endenergie_heizen[0], label="Endenergie Heizen", color="red")
        self.ax.plot(self.endenergie_kühlen[0], label="Endenergie kühlen", color="blue")
        self.ax.set_title(f"Energieverlauf des EZGs um {self.name}")
        self.ax.set_xlabel("Stunden")
        self.ax.set_ylabel("Energie in kWh")
        self.ax.legend()
        self.image_path = "energieverlauf.png"
        self.energieverlauf_plt.savefig(self.image_path)
        self.max_heizenergie = self.endenergie_heizen[1]
        self.max_kühlenergie = self.endenergie_kühlen[1]
        self.jährlicher_heiz_endenergiebedarf = self.endenergie_heizen[2]
        self.jährlicher_kühl_endenergiebedarf = self.endenergie_kühlen[2]



    def heizenergie(self):
        Q = np.zeros(8760)
        for gebäude in self.gebäude_liste.values():
            Q += np.array(gebäude.heizbedarf_zeitreihe)
        return Q, max(Q), sum(Q)



    def kühlenergie(self):
        Q = np.zeros(8760)
        for gebäude in self.gebäude_liste.values():
            Q += np.array(gebäude.kühlbedarf_zeitreihe)
        return Q, abs(min(Q)), abs(sum(Q))
        
    def anzahl_Wohngebäude(self):
        anzahl_WG = 0
        for gebäude in self.gebäude_liste.values():
            if gebäude.category == "Wohnhaus":
                anzahl_WG += 1
        return anzahl_WG