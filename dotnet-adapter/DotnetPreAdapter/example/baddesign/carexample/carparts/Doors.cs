
using Examples.BadDesign;

namespace Examples.BadDesign.CarExample.CarParts {

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
}