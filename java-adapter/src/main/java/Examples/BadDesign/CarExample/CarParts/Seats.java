package Examples.BadDesign.CarExample.CarParts;

import Examples.BadDesign.DB;

public class Seats {
    int comfort;
    int weight;
    DB db;
    Seats(int comfort, int weight, int number) {
        this.comfort = comfort;
        this.weight = weight * number;
    }
    int getWeight() {
        return weight;
    }
}
