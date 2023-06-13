package Examples.BetterDesign.CarExample.CarParts;

import Examples.BetterDesign.DBCar;

public class Doors {
    DBCar db;
    int comfort;
    int weight;
    Doors(int comfort, int weight, int number) {
        this.comfort = comfort;
        this.weight = weight * number;
    }
    int getWeight() {
        return weight;
    }
}
