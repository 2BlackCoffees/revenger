
using Examples.BadDesign;
namespace Examples.BadDesign.CarExample.CarParts {

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
}