package Examples.BetterDesign.CarExample.CarParts;

import Examples.BetterDesign.DBCar;

public class Driver {
    int weight;
    DBCar db;
    public Driver() {

    }
    Driver(int weight) {
        this.weight = weight;
    }
    int getWeight() {
        return weight;
    }
}
