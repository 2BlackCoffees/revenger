package Examples.BetterDesign.Repository.CarExample.CarParts;

import Examples.BetterDesign.Repository.DBCar;

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
