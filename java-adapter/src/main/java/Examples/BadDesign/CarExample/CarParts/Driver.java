package Examples.BadDesign.CarExample.CarParts;

import Examples.BadDesign.DB;

public class Driver {
    int weight;
    DB db;
    public Driver() {

    }
    Driver(int weight) {
        this.weight = weight;
    }
    int getWeight() {
        return weight;
    }
}
