package Examples.BadDesign.CarExample.CarParts;

import Examples.BadDesign.DB;

public class Doors {
    DB db;
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
