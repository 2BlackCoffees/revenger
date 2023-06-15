package Examples.BetterDesign.Repository.CarExample.CarParts;

import Examples.BetterDesign.Repository.DBCar;

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
